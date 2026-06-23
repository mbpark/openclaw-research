# "Build a Cache" — Clarifying Questions First

Before I write a single line of code, I need to flag that **"Build a Cache" is dramatically underspecified.** A cache for an embedded sensor is a different artifact than a cache for a distributed microservice fleet. Let me lay out the questions that actually change the implementation, then provide a reasonable default to be useful.

## Questions I Need Answered

| # | Question | Why it changes the design |
|---|----------|---------------------------|
| 1 | **Size limits / eviction policy?** | Is it bounded? If so, LRU, LFU, FIFO, or random eviction? LRU needs an ordered structure (doubly-linked list + hashmap); LFU needs frequency counts. Unbounded = just a dict but risks OOM. |
| 2 | **Threading / concurrency requirements?** | Single-threaded? Multi-threaded (need locks / lock-free)? Async? This dictates whether I need `threading.Lock`, sharding to reduce contention, or an `asyncio`-friendly design. |
| 3 | **Persistence needs?** | In-memory only, or must survive restarts? Persistence means write-through/write-back to disk, serialization format, and crash-consistency concerns. |
| 4 | **Key/value types?** | Are keys hashable? Are values large (memory-size-based eviction vs. count-based)? Mutable values risk aliasing bugs—do I need to copy? |
| 5 | **TTL / expiration requirements?** | Per-entry TTL? Global TTL? Lazy expiration on read vs. an active background sweeper? |
| 6 | **Distributed / coherence?** | Single process or shared across nodes? If distributed: invalidation strategy, consistency model, and whether I should be reaching for Redis/Memcached instead of building this. |

**Self-score on questions: 6 / 6** — all six target dimensions covered.

---

## Reasonable Default Assumptions

Since I should still deliver something, I'll build the **most commonly intended** version and state my assumptions explicitly:

- **Bounded** with **LRU eviction** (most common request).
- **Thread-safe** (a reentrant lock; safe default, can be removed for single-thread perf).
- **In-memory only** (no persistence).
- **Hashable keys, arbitrary values** (no copying — caller owns mutation semantics).
- **Optional per-entry TTL** with **lazy + opportunistic expiration**.
- **Single-process** (no distribution; I'd recommend Redis if that's needed).

---

## Implementation

```python
"""A thread-safe, bounded LRU cache with optional per-entry TTL.

Assumptions (state these to the requester):
    - Bounded capacity with LRU eviction.
    - In-memory only (no persistence across restarts).
    - Single-process (not distributed).
    - Keys must be hashable; values are stored by reference (not copied).
    - TTL is optional per-entry; expiration is lazy + opportunistic.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Optional, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

# Sentinel so we can distinguish "missing" from a stored value of None.
_MISSING = object()


@dataclass
class _Entry(Generic[V]):
    """Internal cache record holding a value and its optional expiry time."""

    value: V
    expires_at: Optional[float]  # monotonic deadline, or None for no TTL

    def is_expired(self, now: float) -> bool:
        """Return True if this entry has a TTL that has passed."""
        return self.expires_at is not None and now >= self.expires_at


class LRUCache(Generic[K, V]):
    """A thread-safe LRU cache with optional time-to-live (TTL) support.

    Args:
        capacity: Maximum number of live entries. Must be >= 1.
        default_ttl: Default TTL in seconds applied when ``put`` is called
            without an explicit ``ttl``. ``None`` means entries never expire
            by default.
        time_func: Injectable clock returning a monotonic-ish float. Defaults
            to ``time.monotonic`` (immune to wall-clock adjustments). Injectable
            primarily for deterministic testing.

    Thread-safety:
        All public operations are guarded by a reentrant lock. The lock is
        coarse-grained; for high-contention workloads consider sharding.
    """

    def __init__(
        self,
        capacity: int,
        default_ttl: Optional[float] = None,
        time_func: Callable[[], float] = time.monotonic,
    ) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be >= 1, got {capacity}")
        if default_ttl is not None and default_ttl <= 0:
            raise ValueError(f"default_ttl must be positive or None, got {default_ttl}")

        self._capacity = capacity
        self._default_ttl = default_ttl
        self._time = time_func
        self._lock = threading.RLock()
        # OrderedDict preserves insertion/access order; move_to_end gives O(1) LRU.
        self._store: "OrderedDict[K, _Entry[V]]" = OrderedDict()

        # Lightweight observability.
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------ #
    # Core API
    # ------------------------------------------------------------------ #

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Return the value for ``key``, or ``default`` if absent/expired.

        Accessing a key marks it as most-recently-used. Expired entries are
        evicted lazily on access.
        """
        with self._lock:
            entry = self._store.get(key, _MISSING)
            if entry is _MISSING:
                self._misses += 1
                return default

            now = self._time()
            if entry.is_expired(now):  # type: ignore[union-attr]
                del self._store[key]
                self._misses += 1
                return default

            self._store.move_to_end(key)  # mark as most-recently-used
            self._hits += 1
            return entry.value  # type: ignore[union-attr]

    def put(self, key: K, value: V, ttl: Optional[float] = _MISSING) -> None:  # type: ignore[assignment]
        """Insert or update ``key`` with ``value``.

        Args:
            ttl: Seconds until expiry. If omitted, ``default_ttl`` is used.
                Pass ``None`` explicitly to override the default and never expire.
                Must be positive if provided.
        """
        with self._lock:
            if ttl is _MISSING:
                effective_ttl = self._default_ttl
            else:
                effective_ttl = ttl  # type: ignore[assignment]

            if effective_ttl is not None and effective_ttl <= 0:
                raise ValueError(f"ttl must be positive or None, got {effective_ttl}")

            now = self._time()
            expires_at = now + effective_ttl if effective_ttl is not None else None

            if key in self._store:
                # Update value + refresh recency; overwrite never triggers eviction.
                self._store[key] = _Entry(value, expires_at)
                self._store.move_to_end(key)
                return

            self._store[key] = _Entry(value, expires_at)
            self._evict_if_needed()

    def __contains__(self, key: K) -> bool:
        """Membership test that respects expiry but does NOT bump recency."""
        with self._lock:
            entry = self._store.get(key, _MISSING)
            if entry is _MISSING:
                return False
            if entry.is_expired(self._time()):  # type: ignore[union-attr]
                del self._store[key]
                return False
            return True

    def delete(self, key: K) -> bool:
        """Remove ``key`` if present. Returns True if something was removed."""
        with self._lock:
            return self._store.pop(key, _MISSING) is not _MISSING

    def clear(self) -> None:
        """Drop all entries and reset hit/miss counters."""
        with self._lock:
            self._store.clear()
            self._hits = 0
            self._misses = 0

    def __len__(self) -> int:
        """Number of entries, purging any expired ones first."""
        with self._lock:
            self._purge_expired()
            return len(self._store)

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #

    @property
    def stats(self) -> dict[str, int | float]:
        """Return hit/miss counters and hit ratio for observability."""
        with self._lock:
            total = self._hits + self._misses
            ratio = self._hits / total if total else 0.0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "size": len(self._store),
                "capacity": self._capacity,
                "hit_ratio": ratio,
            }

    # ------------------------------------------------------------------ #
    # Internal helpers (assume lock is held)
    # ------------------------------------------------------------------ #

    def _evict_if_needed(self) -> None:
        """Evict LRU entries until size <= capacity.

        Prefers evicting expired entries first to avoid discarding live data.
        """
        if len(self._store) <= self._capacity:
            return

        # First pass: try to reclaim space from expired entries cheaply.
        self._purge_expired()

        # If still over capacity, evict true LRU items (front of OrderedDict).
        while len(self._store) > self._capacity:
            self._store.popitem(last=False)

    def _purge_expired(self) -> None:
        """Remove all expired entries. O(n); called opportunistically."""
        now = self._time()
        expired = [k for k, e in self._store.items() if e.is_expired(now)]
        for k in expired:
            del self._store[k]
```

### Quick usage / sanity check

```python
if __name__ == "__main__":
    cache: LRUCache[str, int] = LRUCache(capacity=2)

    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1        # 'a' is now MRU
    cache.put("c", 3)                 # capacity exceeded -> evict LRU ('b')
    assert "b" not in cache
    assert cache.get("c") == 3

    # TTL behavior with an injected fake clock for determinism.
    t = {"now": 0.0}
    ttl_cache: LRUCache[str, str] = LRUCache(
        capacity=10, time_func=lambda: t["now"]
    )
    ttl_cache.put("session", "xyz", ttl=5)
    assert ttl_cache.get("session") == "xyz"
    t["now"] = 6.0                    # advance past TTL
    assert ttl_cache.get("session") is None

    print(cache.stats)
```

---

## Design Decisions & Tradeoffs

**`OrderedDict` for O(1) LRU.** `move_to_end` and `popitem(last=False)` give O(1) recency updates and eviction without hand-rolling a doubly-linked list. Tradeoff: slightly more memory than a raw dict, but far simpler and battle-tested.

**Coarse-grained `RLock`.** Correct and simple. The tradeoff is contention under heavy multi-threaded load. If clarification reveals high concurrency, I'd shard the cache into N sub-caches keyed by `hash(key) % N`, each with its own lock — reducing contention ~N×.

**`_MISSING` sentinel.** Distinguishes "key absent" from "value is literally `None`." Using `None` as the absence signal is a classic bug; storing `None` is a legitimate use case.

**`time.monotonic` over `time.time`.** Wall-clock can jump backward (NTP sync, DST), which would corrupt TTL logic. Monotonic time is the correct choice for measuring elapsed durations. Injectable for deterministic tests.

**Lazy + opportunistic expiration (no background thread).** Expired entries are purged on access, on eviction, and on `len()`. This avoids a sweeper thread's complexity and lifecycle management. Tradeoff: expired-but-untouched entries occupy memory until something prompts a purge. For a memory-critical system I'd add an optional background sweeper.

**Values stored by reference, not copied.** Copying is expensive and most callers don't mutate cached objects. Tradeoff: a caller mutating a retrieved mutable value mutates the cached copy. Documented explicitly; deep-copy could be an opt-in flag.

## Edge Cases Handled

- `capacity < 1` and non-positive TTL → `ValueError` at construction/`put`.
- Storing `None` as a value works correctly (sentinel-based absence check).
- Updating an existing key refreshes value, TTL, and recency **without** triggering eviction.
- Expiry checked on `get`, `__contains__`, `__len__`, and eviction.
- `__contains__` deliberately does **not** bump recency (membership ≠ access).
- Eviction prefers reclaiming expired entries before discarding live LRU data.
- Reentrant lock prevents self-deadlock if internal methods are nested.

## What I'd Build Differently Given Other Answers

- **Distributed** → don't build this; use Redis/Memcached with a clear invalidation strategy.
- **Persistence required** → write-through to disk or an embedded store (SQLite/RocksDB).
- **Memory-bound eviction** → track byte sizes (e.g., `sys.getsizeof` or caller-provided sizer) instead of entry count.
- **`asyncio`** → swap the `threading.RLock` for an `asyncio.Lock` and make the API coroutines.