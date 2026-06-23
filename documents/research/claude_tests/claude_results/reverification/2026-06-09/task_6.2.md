# "Implement a Database" — Let's Scope This First

Before writing code, I need to flag that **"implement a database" is radically underspecified.** A database can mean anything from a 50-line key-value dict wrapper to a distributed SQL engine with MVCC, WAL, and a query planner. Building the wrong one wastes enormous effort.

Here are the questions I'd ask a stakeholder, with why each one changes the implementation:

## Clarifying Questions

| # | Question | Why it matters / how it changes the design |
|---|----------|--------------------------------------------|
| 1 | **Data model: relational, document, or key-value?** | Relational needs a schema + join/query engine; document needs nested serialization + indexing; KV is the simplest (hash map + persistence). Completely different architectures. |
| 2 | **Schema requirements?** | Fixed schema enables type validation, columnar storage, and constraints. Schemaless means I store opaque blobs and push validation to the app. |
| 3 | **Concurrency needs?** | Single-threaded? Multi-reader/single-writer? Full multi-writer? This dictates whether I need locks, MVCC, or an MVCC + transaction manager. |
| 4 | **Durability guarantees?** | In-memory only? Periodic snapshots? Write-ahead log with `fsync` per commit (ACID-D)? This is the difference between a dict and a storage engine. |
| 5 | **Expected query patterns?** | Point lookups → hash index. Range scans → B-tree/sorted structure. Full-text → inverted index. Analytical aggregations → columnar layout. |
| 6 | **Scale expectations?** | Fits in RAM? Single node on disk? Distributed/sharded? Drives whether I need paging, buffer pools, or a network layer. |

Bonus questions I'd also raise: **transaction/isolation level** (read-committed vs. serializable), **eviction policy** if memory-bounded, and **client interface** (embedded library vs. server protocol).

---

## My Assumed Scope

Since I have to ship *something*, I'll pick a **defensible, well-bounded target** and state assumptions explicitly:

> **A single-node, embedded, persistent key-value store with ACID transactions, configurable durability, concurrent reader/writer access via a write-ahead log + snapshotting, and a simple range-scan index.**

This is a realistic "small but real" database (think a simplified BoltDB/LevelDB). It exercises the interesting parts—durability, concurrency, recovery—without ballooning into a SQL engine.

---

## Implementation

```python
"""
A single-node, embedded, persistent key-value database.

Features:
  - ACID transactions (snapshot isolation via copy-on-write).
  - Durability via a write-ahead log (WAL) with configurable fsync policy.
  - Crash recovery: replay WAL on startup.
  - Concurrency: many readers + single writer (writer serialized by a lock).
  - Range scans via an in-memory sorted index.

Assumptions (stated explicitly because the task was underspecified):
  - Keys and values are strings (UTF-8). Easily generalizable to bytes.
  - Whole dataset fits in memory; WAL + snapshot provide durability.
  - Single process. Not distributed.
"""

from __future__ import annotations

import json
import os
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Optional
import sortedcontainers  # pip install sortedcontainers


class Durability(Enum):
    """Controls when writes are guaranteed to survive a crash."""
    NONE = "none"        # No fsync; fastest, may lose recent commits on crash.
    BATCH = "batch"      # fsync periodically (background); bounded data loss.
    FULL = "full"        # fsync on every commit; slowest, no committed-data loss.


# A WAL record is a tuple of (op, key, value). A tombstone uses value=None.
_PUT = "put"
_DELETE = "delete"


@dataclass
class _WALRecord:
    """A single logged mutation."""
    txn_id: int
    op: str
    key: str
    value: Optional[str]

    def serialize(self) -> str:
        return json.dumps(
            {"t": self.txn_id, "o": self.op, "k": self.key, "v": self.value}
        )

    @staticmethod
    def deserialize(line: str) -> "_WALRecord":
        d = json.loads(line)
        return _WALRecord(d["t"], d["o"], d["k"], d["v"])


class Transaction:
    """
    A transaction providing snapshot isolation.

    Reads see a consistent snapshot taken at transaction start. Writes are
    buffered locally and applied atomically on commit. Read-only transactions
    never block writers and vice-versa.
    """

    def __init__(self, db: "Database", txn_id: int, snapshot: "sortedcontainers.SortedDict[str, str]"):
        self._db = db
        self._txn_id = txn_id
        self._snapshot = snapshot          # consistent view at txn start
        self._writes: dict[str, Optional[str]] = {}  # key -> value or None (delete)
        self._committed = False
        self._closed = False

    def get(self, key: str) -> Optional[str]:
        """Return the value for `key`, honoring this txn's own pending writes."""
        self._check_open()
        if key in self._writes:                 # read-your-own-writes
            return self._writes[key]
        return self._snapshot.get(key)

    def put(self, key: str, value: str) -> None:
        """Stage a write. Not visible to others until commit."""
        self._check_open()
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("keys and values must be str")
        self._writes[key] = value

    def delete(self, key: str) -> None:
        """Stage a deletion."""
        self._check_open()
        self._writes[key] = None

    def scan(self, start: str, end: str) -> Iterator[tuple[str, str]]:
        """
        Yield (key, value) pairs with start <= key < end, in sorted order.

        Merges the snapshot with this transaction's pending writes.
        """
        self._check_open()
        # Merge snapshot view with local writes for a consistent range result.
        merged = dict(self._snapshot.irange(start, end, inclusive=(True, False)) and
                      ((k, self._snapshot[k]) for k in self._snapshot.irange(start, end, inclusive=(True, False))))
        for k, v in self._writes.items():
            if start <= k < end:
                if v is None:
                    merged.pop(k, None)
                else:
                    merged[k] = v
        for k in sorted(merged):
            yield k, merged[k]

    def commit(self) -> None:
        """Atomically persist and apply all staged writes."""
        self._check_open()
        if self._writes:
            self._db._commit_writes(self._txn_id, self._writes)
        self._committed = True
        self._closed = True

    def rollback(self) -> None:
        """Discard staged writes."""
        self._writes.clear()
        self._closed = True

    def _check_open(self) -> None:
        if self._closed:
            raise RuntimeError("transaction already committed or rolled back")


class Database:
    """
    An embedded persistent key-value database.

    Concurrency model:
      - Multiple concurrent read transactions (each gets an immutable snapshot).
      - A single writer at a time (serialized by `_write_lock`).
    This is the classic single-writer/multi-reader model used by BoltDB,
    avoiding write-write conflicts entirely while keeping reads lock-free.
    """

    def __init__(self, path: str, durability: Durability = Durability.FULL,
                 batch_interval_s: float = 1.0):
        self._path = path
        self._wal_path = os.path.join(path, "wal.log")
        self._snapshot_path = os.path.join(path, "snapshot.json")
        self._durability = durability
        self._batch_interval_s = batch_interval_s

        os.makedirs(path, exist_ok=True)

        # The authoritative in-memory store, kept sorted for range scans.
        self._data: sortedcontainers.SortedDict[str, str] = sortedcontainers.SortedDict()
        self._txn_counter = 0

        self._write_lock = threading.Lock()   # serializes writers
        self._data_lock = threading.Lock()    # protects snapshot creation
        self._wal_lock = threading.Lock()     # protects WAL file handle

        self._recover()                        # crash recovery on startup
        self._wal_file = open(self._wal_path, "a", encoding="utf-8")

        self._closed = False
        if durability == Durability.BATCH:
            self._stop_flusher = threading.Event()
            self._flusher = threading.Thread(target=self._batch_flush_loop, daemon=True)
            self._flusher.start()

    # ---------- Public API ----------

    @contextmanager
    def transaction(self) -> Iterator[Transaction]:
        """
        Context-managed transaction. Commits on clean exit, rolls back on error.

        Usage:
            with db.transaction() as txn:
                txn.put("a", "1")
        """
        txn = self.begin()
        try:
            yield txn
            if not txn._closed:
                txn.commit()
        except Exception:
            if not txn._closed:
                txn.rollback()
            raise

    def begin(self) -> Transaction:
        """Start a transaction with a consistent snapshot of the current data."""
        with self._data_lock:
            self._txn_counter += 1
            # Snapshot via shallow copy. Strings are immutable so this is safe;
            # copy-on-the-dict is O(n) but cheap relative to disk I/O for our scale.
            snapshot = sortedcontainers.SortedDict(self._data)
            return Transaction(self, self._txn_counter, snapshot)

    def get(self, key: str) -> Optional[str]:
        """Convenience single-key read (auto-transaction)."""
        with self.transaction() as txn:
            return txn.get(key)

    def put(self, key: str, value: str) -> None:
        """Convenience single-key write (auto-transaction)."""
        with self.transaction() as txn:
            txn.put(key, value)

    def close(self) -> None:
        """Flush, snapshot, and release resources."""
        if self._closed:
            return
        if self._durability == Durability.BATCH:
            self._stop_flusher.set()
            self._flusher.join()
        with self._wal_lock:
            self._wal_file.flush()
            os.fsync(self._wal_file.fileno())
            self._wal_file.close()
        self._compact()  # write snapshot + truncate WAL
        self._closed = True

    # ---------- Internal: commit path ----------

    def _commit_writes(self, txn_id: int, writes: dict[str, Optional[str]]) -> None:
        """
        Durably commit a write set.

        Order matters for crash safety:
          1. Append all records to the WAL.
          2. fsync per durability policy.
          3. Apply to in-memory store (under data_lock).
        If we crash between (2) and (3), recovery replays the WAL.
        """
        with self._write_lock:  # single-writer: prevents write-write conflicts
            records = [
                _WALRecord(txn_id, _PUT if v is not None else _DELETE, k, v)
                for k, v in writes.items()
            ]
            with self._wal_lock:
                for rec in records:
                    self._wal_file.write(rec.serialize() + "\n")
                # commit marker lets recovery know the txn is complete & atomic
                self._wal_file.write(json.dumps({"t": txn_id, "o": "commit"}) + "\n")
                if self._durability == Durability.FULL:
                    self._wal_file.flush()
                    os.fsync(self._wal_file.fileno())
                else:
                    self._wal_file.flush()  # OS buffer; not guaranteed on disk

            # Apply atomically to memory only after it's logged.
            with self._data_lock:
                for k, v in writes.items():
                    if v is None:
                        self._data.pop(k, None)
                    else:
                        self._data[k] = v

    # ---------- Internal: durability & recovery ----------

    def _batch_flush_loop(self) -> None:
        """Background fsync for BATCH durability mode."""
        while not self._stop_flusher.wait(self._batch_interval_s):
            with self._wal_lock:
                self._wal_file.flush()
                os.fsync(self._wal_file.fileno())

    def _recover(self) -> None:
        """
        Rebuild in-memory state from snapshot + WAL replay.

        Only writes belonging to *committed* transactions are applied,
        guaranteeing atomicity (no partial transactions after a crash).
        """
        # 1. Load last snapshot if present.
        if os.path.exists(self._snapshot_path):
            with open(self._snapshot_path, "r", encoding="utf-8") as f:
                for k, v in json.load(f).items():
                    self._data[k] = v

        # 2. Replay WAL, applying only committed transactions.
        if not os.path.exists(self._wal_path):
            return
        pending: dict[int, list[_WALRecord]] = {}
        with open(self._wal_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    # Torn write at end of log (crash mid-append): stop replaying.
                    break
                if d["o"] == "commit":
                    for rec in pending.pop(d["t"], []):
                        if rec.op == _DELETE:
                            self._data.pop(rec.key, None)
                        else:
                            self._data[rec.key] = rec.value
                else:
                    pending.setdefault(d["t"], []).append(_WALRecord.deserialize(line))
        # Uncommitted (no commit marker) records in `pending` are discarded.

    def _compact(self) -> None:
        """Persist full snapshot and truncate the WAL to bound its growth."""
        with self._data_lock, self._wal_lock:
            tmp = self._snapshot_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(dict(self._data), f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self._snapshot_path)  # atomic rename
            # Truncate WAL now that its contents are captured in the snapshot.
            open(self._wal_path, "w").close()


# ---------- Demo / self-test ----------
if __name__ == "__main__":
    import shutil
    test_dir = "/tmp/mydb_demo"
    shutil.rmtree(test_dir, ignore_errors=True)

    db = Database(test_dir, durability=Durability.FULL)
    with db.transaction() as txn:
        txn.put("apple", "1")
        txn.put("banana", "2")
        txn.put("cherry", "3")

    # Snapshot isolation: this read won't see uncommitted concurrent writes.
    print("get apple:", db.get("apple"))
    with db.transaction() as txn:
        print("scan a..c:", list(txn.scan("a", "c")))  # apple, banana

    # Rollback discards writes.
    try:
        with db.transaction() as txn:
            txn.put("apple", "999")
            raise ValueError("simulated failure")
    except ValueError:
        pass
    print("after rollback, apple:", db.get("apple"))  # still "1"

    db.close()

    # Reopen → crash recovery from snapshot + WAL.
    db2 = Database(test_dir)
    print("after reopen, banana:", db2.get("banana"))  # "2"
    db2.close()
```

---

## Design Decisions & Tradeoffs

**1. Single-writer / multi-reader concurrency.**
I serialize writers with one lock and give readers immutable snapshots. This is exactly BoltDB's model. **Pro:** no write-write conflicts, no deadlocks, lock-free reads. **Con:** no write parallelism — fine for read-heavy workloads, a bottleneck for write-heavy ones (where I'd move to MVCC with per-key versioning + optimistic concurrency control).

**2. Snapshot isolation via copy-on-begin.**
`begin()` shallow-copies the SortedDict. Strings are immutable so sharing is safe. **Tradeoff:** copy is O(n) memory/time per txn — acceptable at small scale but I'd switch to a persistent/immutable data structure (HAMT or a copy-on-write B-tree) to make snapshots O(1).

**3. WAL + snapshot for durability.**
Writes go to the log *before* memory, with a `commit` marker delimiting atomic transactions. Recovery replays only committed txns. The `Durability` enum lets the caller trade safety for speed (`FULL` = fsync per commit, `BATCH` = bounded loss, `NONE` = fastest). This is the standard ACID-D mechanism.

**4. JSON serialization.**
Chosen for readability/debuggability over speed. In production I'd use a length-prefixed binary format with CRC checksums per record to detect corruption robustly.

## Edge Cases Handled

- **Crash mid-write (torn log line):** recovery `break`s on the first un-parseable line and discards the partial tail.
- **Crash mid-transaction:** records without a `commit` marker are discarded → atomicity preserved.
- **Atomic snapshot write:** write-to-temp + `os.replace` (atomic rename) so a crash during compaction never corrupts the snapshot.
- **Read-your-own-writes:** `get`/`scan` merge pending writes over the snapshot.
- **Double commit/rollback:** guarded by `_check_open`.
- **Exception inside `with`:** auto-rollback via the context manager.
- **Type validation:** non-string keys/values rejected at `put`.

## Known Limitations (what I'd build next given more scope)

The `scan` merge is O(n log n) and the snapshot copy is O(n) — both fine for in-memory scale but the first things I'd optimize. No distributed support, no SQL/query layer, and BATCH mode's background fsync isn't coordinated with `commit` return (so a "committed" call can still lose data within `batch_interval_s` — that's the documented contract). These are all deliberate scope cuts driven by the assumptions I stated up front.