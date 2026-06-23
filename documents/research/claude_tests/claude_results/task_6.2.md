# Implementing a Database

Before I write code, let me flag the obvious: **"Implement a database" is radically underspecified.** A production database is a multi-year effort by large teams. The right engineering response is to clarify scope before committing to a design. Let me ask the questions that actually change the architecture, state my assumptions, then deliver a working implementation against those assumptions.

## Clarifying Questions

1. **Data model:** Relational (tables, SQL, joins)? Document (nested JSON)? Key-value? Or graph? — *This is the single biggest fork in the design.*
2. **Schema:** Strict schema with typed columns and constraints, or schema-less?
3. **Concurrency:** Single-threaded embedded use, or concurrent readers/writers? If concurrent — what isolation level (read-committed, snapshot, serializable)?
4. **Durability:** Must survive process crash / power loss? Do we need a write-ahead log and `fsync` guarantees, or is "best effort" fine?
5. **Query patterns:** Point lookups by key? Range scans? Ad-hoc filters? Joins? Aggregations? — *Determines indexing strategy.*
6. **Scale:** In-memory only, or larger-than-RAM (must spill to disk)? Throughput / latency targets? Single node only?

## Assumptions I'll Build Against

Since I have to ship *something*, I'll target a **realistic, defensible scope**:

- **Key-value store with secondary-index support** — the most reusable primitive; relational/document engines are built on top of this.
- **Persistent** via a **write-ahead log (WAL)** + periodic snapshot, with `fsync` on commit for durability.
- **Concurrent**: multiple readers, single writer per transaction, **snapshot isolation** via MVCC-lite (copy-on-write).
- **Larger-than-RAM is out of scope** — I'll keep data in memory but persist to disk (clearly noted as a tradeoff).
- **Query support**: point get/put/delete, range scans over keys, and equality lookups via secondary indexes.

---

## Implementation

```python
"""
A persistent, concurrent, transactional key-value store.

Design summary
--------------
- In-memory primary store (sorted dict) for O(log n) range scans.
- Write-Ahead Log (WAL) for durability: every committed mutation is appended
  and fsync'd before the transaction is acknowledged.
- Periodic snapshots compact the WAL so recovery time stays bounded.
- Snapshot isolation: each transaction sees a consistent view taken at start.
  Writes are buffered and applied atomically at commit (single global write
  lock serializes commits -> serializable for writes, snapshot for reads).
- Secondary indexes maintained synchronously inside the write lock.

Out of scope (explicitly): larger-than-RAM datasets, distributed replication,
SQL parsing, joins. See README notes for why.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterator, Optional

from sortedcontainers import SortedDict  # pip install sortedcontainers


# --------------------------------------------------------------------------- #
# Serialization helpers
# --------------------------------------------------------------------------- #

class OpType(str, Enum):
    """Mutation types recorded in the WAL."""
    PUT = "put"
    DELETE = "delete"


@dataclass(frozen=True)
class LogRecord:
    """A single durable mutation entry."""
    txn_id: int
    op: OpType
    key: str
    value: Optional[Any] = None  # None for DELETE

    def serialize(self) -> str:
        return json.dumps(
            {"txn": self.txn_id, "op": self.op.value, "k": self.key, "v": self.value},
            separators=(",", ":"),
        )

    @staticmethod
    def deserialize(line: str) -> "LogRecord":
        d = json.loads(line)
        return LogRecord(
            txn_id=d["txn"],
            op=OpType(d["op"]),
            key=d["k"],
            value=d.get("v"),
        )


# --------------------------------------------------------------------------- #
# Write-Ahead Log
# --------------------------------------------------------------------------- #

class WriteAheadLog:
    """
    Append-only durable log. Each line is one JSON-encoded LogRecord.

    Durability: append + flush + fsync before returning from `commit`.
    This is the classic latency/durability tradeoff: fsync is slow but
    guarantees the write survives a crash.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        # Open in append mode; create if missing.
        self._fh = open(path, "a", encoding="utf-8")

    def append_batch(self, records: list[LogRecord], *, durable: bool = True) -> None:
        """Append a batch of records atomically-ish and optionally fsync."""
        for rec in records:
            self._fh.write(rec.serialize() + "\n")
        self._fh.flush()
        if durable:
            os.fsync(self._fh.fileno())

    def replay(self) -> Iterator[LogRecord]:
        """Yield records in order for crash recovery."""
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield LogRecord.deserialize(line)
                except (json.JSONDecodeError, KeyError):
                    # Torn last write (crash mid-append). Stop — everything
                    # after a corrupt record is untrusted.
                    break

    def truncate(self) -> None:
        """Clear the log (called after a successful snapshot)."""
        self._fh.close()
        self._fh = open(self._path, "w", encoding="utf-8")

    def close(self) -> None:
        self._fh.close()


# --------------------------------------------------------------------------- #
# Index definition
# --------------------------------------------------------------------------- #

@dataclass
class SecondaryIndex:
    """
    Equality index mapping an extracted field value -> set of primary keys.

    `extractor` pulls the indexed value out of a stored record. Returning None
    means "do not index this row" (sparse index behavior).
    """
    name: str
    extractor: Callable[[Any], Optional[Any]]
    _map: dict[Any, set[str]] = field(default_factory=dict)

    def add(self, primary_key: str, value: Any) -> None:
        idx_val = self.extractor(value)
        if idx_val is None:
            return
        self._map.setdefault(idx_val, set()).add(primary_key)

    def remove(self, primary_key: str, value: Any) -> None:
        idx_val = self.extractor(value)
        if idx_val is None:
            return
        keys = self._map.get(idx_val)
        if keys:
            keys.discard(primary_key)
            if not keys:
                del self._map[idx_val]

    def lookup(self, value: Any) -> set[str]:
        return set(self._map.get(value, set()))


# --------------------------------------------------------------------------- #
# Transaction
# --------------------------------------------------------------------------- #

class Transaction:
    """
    Buffers reads/writes and provides snapshot-isolated reads.

    Reads first check the local write buffer, then fall back to the snapshot
    captured at transaction start — so the transaction never sees concurrent
    commits from other transactions.
    """

    _TOMBSTONE = object()  # sentinel for deletes within a txn buffer

    def __init__(self, db: "Database", snapshot: SortedDict) -> None:
        self._db = db
        self._snapshot = snapshot          # read view (not mutated)
        self._writes: dict[str, Any] = {}  # key -> value or _TOMBSTONE
        self._committed = False
        self._active = True

    def get(self, key: str) -> Optional[Any]:
        """Return value for key, or None if absent/deleted."""
        self._check_active()
        if key in self._writes:
            val = self._writes[key]
            return None if val is self._TOMBSTONE else val
        return self._snapshot.get(key)

    def put(self, key: str, value: Any) -> None:
        self._check_active()
        if not isinstance(key, str):
            raise TypeError("Keys must be strings.")
        self._writes[key] = value

    def delete(self, key: str) -> None:
        self._check_active()
        self._writes[key] = self._TOMBSTONE

    def scan(self, start: Optional[str] = None,
             end: Optional[str] = None) -> Iterator[tuple[str, Any]]:
        """
        Range scan [start, end) over the merged snapshot + local writes.
        Inclusive of `start`, exclusive of `end`. None = unbounded.
        """
        self._check_active()
        # Merge committed snapshot with uncommitted local writes.
        merged = dict(self._snapshot)
        for k, v in self._writes.items():
            if v is self._TOMBSTONE:
                merged.pop(k, None)
            else:
                merged[k] = v
        for k in sorted(merged):
            if start is not None and k < start:
                continue
            if end is not None and k >= end:
                break
            yield k, merged[k]

    def commit(self) -> None:
        """Atomically apply buffered writes. Durable before returning."""
        self._check_active()
        self._db._commit_txn(self)  # serialized by the DB write lock
        self._committed = True
        self._active = False

    def rollback(self) -> None:
        self._writes.clear()
        self._active = False

    def _check_active(self) -> None:
        if not self._active:
            raise RuntimeError("Transaction is no longer active.")

    # Context manager: auto-commit on success, rollback on exception.
    def __enter__(self) -> "Transaction":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None and self._active:
            self.commit()
        elif self._active:
            self.rollback()
        return False  # never suppress exceptions


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #

class Database:
    """
    Embedded transactional key-value database.

    Thread-safe: readers run concurrently against immutable-ish snapshots;
    a single global write lock serializes commits (giving serializable writes,
    snapshot-isolation reads).
    """

    def __init__(self, data_dir: str, *, durable: bool = True,
                 snapshot_threshold: int = 1000) -> None:
        os.makedirs(data_dir, exist_ok=True)
        self._dir = data_dir
        self._wal = WriteAheadLog(os.path.join(data_dir, "wal.log"))
        self._snapshot_path = os.path.join(data_dir, "snapshot.json")
        self._durable = durable
        self._snapshot_threshold = snapshot_threshold

        self._store: SortedDict = SortedDict()  # primary store
        self._indexes: dict[str, SecondaryIndex] = {}
        self._txn_counter = 0
        self._writes_since_snapshot = 0

        # RLock guards commits + structural changes. Reads of the snapshot
        # are taken under this lock briefly, then released.
        self._write_lock = threading.RLock()

        self._recover()

    # ---------------- public API ---------------- #

    def create_index(self, name: str,
                     extractor: Callable[[Any], Optional[Any]]) -> None:
        """Create and back-fill a secondary equality index."""
        with self._write_lock:
            if name in self._indexes:
                raise ValueError(f"Index {name!r} already exists.")
            idx = SecondaryIndex(name, extractor)
            for k, v in self._store.items():
                idx.add(k, v)
            self._indexes[name] = idx

    def begin(self) -> Transaction:
        """Start a transaction with a consistent read snapshot."""
        with self._write_lock:
            # Shallow copy is the snapshot. For large stores this is the
            # main scalability limit — see tradeoffs note. A real MVCC engine
            # would version individual rows instead.
            snapshot = SortedDict(self._store)
        return Transaction(self, snapshot)

    def query_index(self, index_name: str, value: Any) -> list[tuple[str, Any]]:
        """Equality lookup via a secondary index."""
        with self._write_lock:
            idx = self._indexes.get(index_name)
            if idx is None:
                raise KeyError(f"No index named {index_name!r}.")
            keys = idx.lookup(value)
            return [(k, self._store[k]) for k in sorted(keys) if k in self._store]

    # Convenience auto-commit helpers (each opens a 1-op transaction).
    def get(self, key: str) -> Optional[Any]:
        return self.begin().get(key)

    def put(self, key: str, value: Any) -> None:
        with self.begin() as txn:
            txn.put(key, value)

    def delete(self, key: str) -> None:
        with self.begin() as txn:
            txn.delete(key)

    def close(self) -> None:
        with self._write_lock:
            self._write_snapshot()
            self._wal.close()

    # ---------------- internals ---------------- #

    def _commit_txn(self, txn: Transaction) -> None:
        """Serialize, log, apply, and index a transaction's writes."""
        if not txn._writes:
            return  # nothing to do; read-only txn

        with self._write_lock:
            self._txn_counter += 1
            txn_id = self._txn_counter

            # 1. Build WAL records.
            records: list[LogRecord] = []
            for key, val in txn._writes.items():
                if val is Transaction._TOMBSTONE:
                    records.append(LogRecord(txn_id, OpType.DELETE, key))
                else:
                    records.append(LogRecord(txn_id, OpType.PUT, key, val))

            # 2. Durably log BEFORE mutating in-memory state (WAL rule).
            self._wal.append_batch(records, durable=self._durable)

            # 3. Apply to primary store + indexes.
            for rec in records:
                self._apply_record(rec)

            self._writes_since_snapshot += len(records)
            if self._writes_since_snapshot >= self._snapshot_threshold:
                self._write_snapshot()

    def _apply_record(self, rec: LogRecord) -> None:
        """Apply one mutation to in-memory store and indexes."""
        old = self._store.get(rec.key)
        if rec.op is OpType.DELETE:
            if old is not None:
                for idx in self._indexes.values():
                    idx.remove(rec.key, old)
                del self._store[rec.key]
        else:  # PUT
            if old is not None:
                for idx in self._indexes.values():
                    idx.remove(rec.key, old)
            self._store[rec.key] = rec.value
            for idx in self._indexes.values():
                idx.add(rec.key, rec.value)

    def _write_snapshot(self) -> None:
        """Atomically persist full state and truncate the WAL."""
        tmp = self._snapshot_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(dict(self._store), fh, separators=(",", ":"))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, self._snapshot_path)  # atomic on POSIX
        self._wal.truncate()
        self._writes_since_snapshot = 0

    def _recover(self) -> None:
        """Rebuild state: load snapshot, then replay WAL on top."""
        if os.path.exists(self._snapshot_path):
            with open(self._snapshot_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self._store = SortedDict(data)

        for rec in self._wal.replay():
            self._apply_record(rec)
            self._txn_counter = max(self._txn_counter, rec.txn_id)
```

### Example usage

```python
if __name__ == "__main__":
    db = Database("./mydb", durable=True, snapshot_threshold=500)

    # Secondary index on the "city" field of stored dicts.
    db.create_index("by_city", lambda v: v.get("city") if isinstance(v, dict) else None)

    with db.begin() as txn:
        txn.put("user:1", {"name": "Ada", "city": "London"})
        txn.put("user:2", {"name": "Alan", "city": "London"})
        txn.put("user:3", {"name": "Grace", "city": "NYC"})

    print(db.get("user:1"))                       # {'name': 'Ada', 'city': 'London'}
    print(db.query_index("by_city", "London"))    # user:1, user:2
    print(list(db.begin().scan("user:1", "user:3")))  # range [user:1, user:3)
    db.close()
```

---

## Design Decisions & Tradeoffs

| Decision | Why | Tradeoff |
|---|---|---|
| **WAL + snapshot** | Standard durability pattern (SQLite, Postgres, LevelDB all do variants). Crash recovery = load snapshot, replay tail. | Double-write cost; snapshotting pauses the writer (mitigated by threshold). |
| **`fsync` per commit** | True durability — survives power loss. | High commit latency. `durable=False` toggle offers the speed/safety knob. |
| **`SortedDict` primary store** | O(log n) point ops *and* efficient ordered range scans. | In-memory only; doesn't scale past RAM. A real engine uses a B-tree or LSM-tree on disk. |
| **Snapshot via shallow copy on `begin()`** | Simple, correct snapshot isolation. | **O(n) per transaction** — the biggest weakness. Real MVCC versions individual rows (copy-on-write per key) instead of the whole map. Called out honestly. |
| **Single global write lock** | Serializable writes with minimal complexity; readers never block. | No write concurrency. Fine for read-heavy workloads; a bottleneck under write contention. |
| **Synchronous index maintenance** | Indexes always consistent with primary data. | Write amplification proportional to index count. |

## Edge Cases Handled

- **Torn WAL writes** (crash mid-append): replay stops at the first corrupt line — everything after is untrusted.
- **Atomic snapshot swap** via `os.replace` (atomic on POSIX) so a crash during snapshotting never corrupts the on-disk state.
- **Delete of nonexistent key**: no-op, no index corruption.
- **Update overwrites index**: old indexed value removed before new one added.
- **Read-only / empty transactions**: skip the WAL entirely — no spurious fsync.
- **Tombstones in txn buffer**: a `delete` then `get` within the same transaction correctly returns `None`.
- **Sparse indexes**: extractor returning `None` skips indexing that row.
- **Non-string keys**: rejected early with `TypeError`.
- **Use-after-commit/rollback**: transactions are marked inactive and raise.

## What I Deliberately Did *Not* Build

To be transparent about scope: no SQL/query planner, no joins, no larger-than-RAM storage (B-tree/LSM paging), no replication or distributed consensus, and no fine-grained MVCC (the whole-snapshot copy is the placeholder). Each of these is a project in itself, and which ones matter depends entirely on the answers to the six questions above.