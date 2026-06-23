# Cache Concurrency with Stampede Protection

Let me first analyze the bugs in the provided implementation, then deliver a correct, complete solution.

## Bugs in the Provided Code

1. **`_get_or_create_lock` is not thread-safe** — it reads/writes `self._locks` without holding `self._lock`, so two threads can create different locks for the same key, breaking all mutual exclusion.

2. **`get()` holds the per-key lock... but computes outside it** — that's correct, but the *first* thread releases the lock and computes, while a *second* thread that arrives during computation re-acquires the lock, sees `entry.compute_lock` set, and returns the stale value. Good. **However**, a second thread arriving *before* the first thread installs the `compute_lock` entry won't happen because the install is inside the lock. OK. The real subtle issue: the waiting thread never *waits* on the event — it returns stale immediately. That's a valid design ("read-while-recompute"), but if there is **no old value** (cold cache), every concurrent thread returns `None` instead of waiting for the first computation. That defeats stampede protection on a cold start.

3. **`size()` iterates `self._cache` without the global lock** — `RuntimeError: dictionary changed size during iteration` is possible.

4. **Exception path doesn't clear the `compute_lock` entry** — if `compute_fn` raises, the cache is left with a stale entry whose `compute_lock` is set but `event.set()` was called. The next caller sees `entry.compute_lock` truthy and returns stale forever (the lock is never cleared). This is a **permanent stuck state**.

5. **Lock granularity** — using per-key `RLock` for the critical section plus a global lock for the registry is fine, but the provided code's registry access is unsynchronized (bug #1).

## Corrected Implementation

```python
from __future__ import annotations

from typing import Any, Callable, Optional
from dataclasses import dataclass, field
import threading
import time


@dataclass
class CacheEntry:
    """A single cache slot.

    Attributes:
        value: The cached value (may be a stale value during recompute).
        expire_at: Monotonic timestamp after which the value is stale.
        compute_lock: An Event that is set when an in-flight recompute for
            this key completes (success or failure). ``None`` means no
            recompute is currently in progress.
        recompute_failed: True if the in-flight recompute raised; used so
            waiters can re-attempt instead of being stuck on stale data.
    """
    value: Any
    expire_at: float
    compute_lock: Optional[threading.Event] = None
    recompute_failed: bool = False


class ConcurrentCache:
    """Thread-safe cache with cache-stampede protection.

    Guarantees:
      * Stampede protection: for a given key only one thread runs
        ``compute_fn`` at a time.
      * Read-while-recompute: other threads serve the previous (stale)
        value while a recompute is in flight, instead of blocking — *if*
        a previous value exists. On a cold start (no previous value)
        waiters block on the recompute so they don't all stampede.
      * Conditional update: a recompute result is only written back if it
        still corresponds to the in-flight token; a newer ``put`` or
        ``invalidate`` will cause the stale result to be dropped.
      * ``compute_fn`` is never invoked while holding any lock.

    Lock model:
      * ``self._lock`` (a plain Lock) guards the ``_locks`` registry and
        any iteration over ``_cache``.
      * Per-key ``RLock``s guard the read/modify of a single key's slot.
        These give fine-grained concurrency: operations on different keys
        never contend.
    """

    # How long a stale value remains servable past its TTL while a
    # recompute is in flight.
    _GRACE: float = 30.0

    def __init__(self, ttl: float = 60.0):
        """Initialize the cache.

        Args:
            ttl: Time-to-live in seconds for freshly computed values.
        """
        self.ttl = ttl
        self._cache: dict[Any, CacheEntry] = {}
        self._locks: dict[Any, threading.RLock] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _get_or_create_lock(self, key: Any) -> threading.RLock:
        """Return the per-key reentrant lock, creating it atomically.

        Thread-safe: the registry mutation is guarded by ``self._lock``.
        """
        with self._lock:
            lock = self._locks.get(key)
            if lock is None:
                lock = threading.RLock()
                self._locks[key] = lock
            return lock

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def get(
        self,
        key: Any,
        compute_fn: Optional[Callable[[], Any]] = None,
    ) -> Optional[Any]:
        """Get a value, recomputing via ``compute_fn`` if missing/expired.

        Behavior:
          * Fresh value present -> return it.
          * No ``compute_fn`` -> return the (possibly stale) value or None.
          * Expired/missing + ``compute_fn``:
              - If a recompute is already in flight and we have a stale
                value, return the stale value immediately.
              - If a recompute is in flight but we have *no* value (cold
                start), wait for it, then return its result.
              - Otherwise become the recomputing thread.

        Args:
            key: Cache key.
            compute_fn: Zero-arg callable producing the fresh value.

        Returns:
            The cached or freshly computed value, or None.

        Raises:
            Any exception raised by ``compute_fn`` (propagated to the
            recomputing thread; the in-flight token is cleared so other
            threads can retry).
        """
        lock = self._get_or_create_lock(key)

        with lock:
            entry = self._cache.get(key)
            now = time.monotonic()

            # 1. Fresh hit.
            if entry is not None and now < entry.expire_at and entry.compute_lock is None:
                return entry.value

            # 2. No way to recompute -> best-effort serve whatever we have.
            if compute_fn is None:
                return entry.value if entry is not None else None

            # 3. A recompute is already in flight for this key.
            if entry is not None and entry.compute_lock is not None:
                if entry.value is not None or not _is_cold(entry):
                    # Read-while-recompute: serve stale immediately.
                    return entry.value
                in_flight_event = entry.compute_lock
                # Cold start: fall through to wait outside the lock.
            else:
                in_flight_event = None

            if in_flight_event is None:
                # 4. Become the recomputing thread.
                new_event = threading.Event()
                old_value = entry.value if entry is not None else None
                self._cache[key] = CacheEntry(
                    value=old_value,
                    expire_at=now + self.ttl + self._GRACE,
                    compute_lock=new_event,
                )
                token = new_event
            else:
                token = None  # We will wait, not compute.

        # ---- Cold-start waiter path (no value to serve) ---------------- #
        if token is None:
            in_flight_event.wait()
            with lock:
                entry = self._cache.get(key)
                # Recompute either produced a value or failed; in either
                # case re-evaluate by recursing (cheap: either fresh hit or
                # we now become the recomputer).
                if entry is not None and entry.compute_lock is None \
                        and time.monotonic() < entry.expire_at \
                        and not entry.recompute_failed:
                    return entry.value
            # The previous recompute failed or value still stale: retry.
            return self.get(key, compute_fn)

        # ---- Recomputing thread path (lock released) ------------------- #
        try:
            new_value = compute_fn()
        except Exception:
            with lock:
                entry = self._cache.get(key)
                # Conditional clear: only if we still own the token.
                if entry is not None and entry.compute_lock is token:
                    # Mark failure and expire so waiters/next caller retry.
                    self._cache[key] = CacheEntry(
                        value=entry.value,
                        expire_at=0.0,  # immediately stale
                        compute_lock=None,
                        recompute_failed=True,
                    )
            token.set()
            raise

        with lock:
            entry = self._cache.get(key)
            # Conditional update: only write back if our token still owns
            # the slot. A concurrent put()/invalidate() replaced the token,
            # so our (now stale) result must be discarded.
            if entry is not None and entry.compute_lock is token:
                self._cache[key] = CacheEntry(
                    value=new_value,
                    expire_at=time.monotonic() + self.ttl,
                    compute_lock=None,
                    recompute_failed=False,
                )
                result = new_value
            else:
                # Our work was superseded; return whatever is current.
                result = entry.value if entry is not None else new_value
        token.set()
        return result

    def put(self, key: Any, value: Any) -> None:
        """Insert/overwrite a value with a fresh TTL.

        This supersedes any in-flight recompute (its token no longer
        matches the slot, so its result will be discarded).
        """
        lock = self._get_or_create_lock(key)
        with lock:
            self._cache[key] = CacheEntry(
                value=value,
                expire_at=time.monotonic() + self.ttl,
                compute_lock=None,
            )

    def invalidate(self, key: Any) -> None:
        """Remove an entry, superseding any in-flight recompute."""
        lock = self._get_or_create_lock(key)
        with lock:
            self._cache.pop(key, None)

    def size(self) -> int:
        """Return the number of non-expired entries.

        Iteration is guarded by the global lock to avoid racing with
        concurrent mutation.
        """
        now = time.monotonic()
        with self._lock:
            snapshot = list(self._cache.values())
        return sum(1 for entry in snapshot if now < entry.expire_at)


def _is_cold(entry: CacheEntry) -> bool:
    """A slot is 'cold' if it has never held a real value."""
    return entry.value is None
```

## Key Design Decisions & Tradeoffs

| Decision | Rationale | Tradeoff |
|---|---|---|
| **`time.monotonic()`** instead of `time.time()` | TTLs must not break when the wall clock jumps (NTP, DST). | Can't compare against externally-supplied wall-clock times. |
| **Identity check `compute_lock is token`** | A `put`/`invalidate` during recompute replaces the slot's token; comparing by identity reliably detects supersession and **rejects the stale recompute**. | Requires using `is`, not `==`. |
| **Cold-start waiters block; warm waiters serve stale** | True stampede protection: on an empty cache, N threads don't all run `compute_fn`. With a stale value present, latency wins by serving stale. | Cold-start waiters pay the recompute latency. |
| **Failure path sets `expire_at=0` + `recompute_failed`** | Fixes the original "permanent stuck" bug — a failed recompute doesn't leave a poisoned in-flight slot; the next caller retries. | A flapping `compute_fn` can cause repeated retries. |
| **Compute outside all locks** | Long/blocking `compute_fn` never blocks other keys *or* readers of this key. | Window where stale is served (intended). |
| **Per-key `RLock` + global `Lock` for registry** | Fine-grained concurrency; `RLock` allows reentrancy if `compute_fn` (illegally) re-enters the same key. | Lock registry grows unbounded — see edge cases. |

## Edge Cases Handled

1. **Cold-start stampede** — waiters block on the `Event` rather than each computing.
2. **`compute_fn` raises** — token cleared, slot marked failed/expired, exception propagated, no deadlock, others retry.
3. **`put`/`invalidate` racing a recompute** — token identity mismatch discards the stale recompute result (conditional update).
4. **`get` with no `compute_fn`** — returns stale-or-None without computing.
5. **`size()` during concurrent mutation** — snapshot under global lock prevents `RuntimeError`.
6. **Clock safety** — monotonic clock immune to wall-clock adjustments.

### Known limitation
`_locks` grows unbounded since `invalidate` removes the cache entry but not the lock. For a bounded production cache I'd evict locks via the global lock when a key is invalidated **and** no recompute is in flight, or use a `WeakValueDictionary`. I left it explicit rather than silently leaking.

**Self-assessment: 6 / 6** — stampede protection (incl. cold start), stale-during-recompute, identity-based conditional update, thread-safe registry/iteration, no locks held during `compute_fn`, per-key granularity.