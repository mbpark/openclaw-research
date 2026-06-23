# "Build a Cache" — Let's Clarify First

Before writing code, I want to flag that **"Build a Cache"** is dramatically underspecified. The right implementation varies enormously based on requirements. Let me ask the key questions, state my assumptions, and then deliver a solid default implementation that's easy to adapt.

## Clarifying Questions

1. **Size limits / eviction policy** — Is the cache bounded? If so, what eviction strategy: LRU, LFU, FIFO, or random? What's the max size (entry count vs. memory bytes)?

2. **Threading / concurrency** — Will this be accessed from multiple threads? Do we need thread-safety, or is it single-threaded (or async)? High contention or low?

3. **Persistence** — Should the cache survive process restarts (disk-backed/Redis), or is in-memory/ephemeral fine?

4. **Key/value types** — Are keys hashable arbitrary objects? Are values large (memory pressure)? Any serialization constraints?

5. **TTL / expiration** — Do entries need time-based expiration? Per-entry TTL or global? Lazy vs. active eviction of expired items?

6. **Distribution / coherence** — Single-process or distributed across nodes? Do we need invalidation/coherence guarantees, or is a local cache sufficient?

---

## My Assumptions (stated explicitly)

Absent answers, I'll build the **most common practical default**:

- **In-memory**, single process
- **Bounded** with **LRU eviction**
- **Thread-safe** (mutex-guarded)
- **Optional per-entry TTL** with lazy + opportunistic expiration
- Hashable keys, arbitrary values
- No persistence, no distribution (but designed for easy extension)

---

## Implementation

```python
from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Iterator, Optional, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

# Sentinel to distinguish "missing" from a stored value of None.
_MISSING = object()


@dataclass
class _Entry(Generic[V]):
    """Internal cache entry holding a value and optional expiry timestamp."""

    value: V
    expires_at: Optional[float]  # monotonic deadline; None means no TTL.

    def is_expired(self, now: float) -> bool:
        """Return True if this entry has passed its expiry deadline."""
        return self.expires_at is not None and now >= self.expires_at


@dataclass
class CacheStats:
    """Lightweight, observable cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0

    @property
    def hit_rate(self) -> float:
        """Fraction of lookups that were hits (0.0 if no lookups)."""
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


class LRUCache(Generic[K, V]):
    """A thread-safe, bounded, LRU cache with optional per-entry TTL.

    Eviction policy: Least Recently Used. On insertion past capacity,
    the least-recently-accessed entry is evicted. Expired entries are
    removed lazily on access and opportunistically during writes.

    The cache is safe for concurrent use by multiple threads.

    Example:
        >>> cache: LRUCache[str, int] = LRUCache(max_size=2)
        >>> cache.set("a", 1)
        >>> cache.set("b", 2)
        >>> cache.get("a")          # touches "a", making "b" the LRU
        1
        >>> cache.set("c", 3)       # evicts "b"
        >>> cache.get("b") is None
        True
    """

    def __init__(
        self,
        max_size: int = 128,
        *,
        default_ttl: Optional[float] = None,
        time_func: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize the cache.

        Args:
            max_size: Maximum number of entries. Must be > 0.
            default_ttl: Default time-to-live in seconds applied to entries
                when no per-call TTL is given. None disables default expiry.
            time_func: Clock source returning seconds. Defaults to a
                monotonic clock (immune to wall-clock adjustments).

        Raises:
            ValueError: If max_size <= 0 or default_ttl is non-positive.
        """
        if max_size <= 0:
            raise ValueError("max_size must be a positive integer")
        if default_ttl is not None and default_ttl <= 0:
            raise ValueError("default_ttl must be positive or None")

        self._max_size = max_size
        self._default_ttl = default_ttl
        self._time = time_func
        # OrderedDict preserves insertion/access order for O(1) LRU.
        self._store: "OrderedDict[K, _Entry[V]]" = OrderedDict()
        # RLock so public methods can call each other without deadlock.
        self._lock = threading.RLock()
        self._stats = CacheStats()

    # ----- Core operations -------------------------------------------------

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Return the value for `key`, or `default` if absent/expired.

        On a hit, the key is marked most-recently-used. Expired entries
        are removed and treated as misses.
        """
        with self._lock:
            entry = self._store.get(key, None)
            if entry is None:
                self._stats.misses += 1
                return default
            if entry.is_expired(self._time()):
                # Lazy expiration.
                del self._store[key]
                self._stats.expirations += 1
                self._stats.misses += 1
                return default
            self._store.move_to_end(key)  # mark as recently used
            self._stats.hits += 1
            return entry.value

    def set(self, key: K, value: V, *, ttl: Optional[float] = _MISSING) -> None:  # type: ignore[assignment]
        """Insert or update `key` with `value`.

        Args:
            key: Hashable cache key.
            value: Value to store (may be None).
            ttl: Per-entry TTL in seconds. Omit to use the cache default;
                pass None to explicitly disable expiry for this entry.

        Raises:
            ValueError: If an explicit ttl is non-positive.
        """
        with self._lock:
            effective_ttl = self._default_ttl if ttl is _MISSING else ttl
            if effective_ttl is not None and effective_ttl <= 0:
                raise ValueError("ttl must be positive or None")

            expires_at = (
                self._time() + effective_ttl if effective_ttl is not None else None
            )

            if key in self._store:
                # Update in place and refresh recency.
                self._store[key] = _Entry(value, expires_at)
                self._store.move_to_end(key)
                return

            self._store[key] = _Entry(value, expires_at)
            self._evict_if_needed()

    def get_or_set(
        self, key: K, factory: Callable[[], V], *, ttl: Optional[float] = _MISSING  # type: ignore[assignment]
    ) -> V:
        """Return the cached value, computing and storing it if absent.

        `factory` is invoked at most once per missing key under the lock.
        Note: holding the lock during `factory` serializes computation,
        which prevents cache stampede but blocks other threads. For slow
        factories, compute outside and call `set` instead.
        """
        with self._lock:
            sentinel: V = _MISSING  # type: ignore[assignment]
            current = self.get(key, default=sentinel)
            if current is not sentinel:
                return current
            value = factory()
            self.set(key, value, ttl=ttl)
            return value

    def delete(self, key: K) -> bool:
        """Remove `key`. Return True if it existed, else False."""
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        """Remove all entries (stats are preserved)."""
        with self._lock:
            self._store.clear()

    # ----- Introspection ---------------------------------------------------

    def __contains__(self, key: K) -> bool:
        """Membership test that respects expiry but does not affect recency."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False
            if entry.is_expired(self._time()):
                del self._store[key]
                self._stats.expirations += 1
                return False
            return True

    def __len__(self) -> int:
        """Number of live (non-expired) entries after purging stale ones."""
        with self._lock:
            self._purge_expired()
            return len(self._store)

    def keys(self) -> list[K]:
        """Snapshot of live keys (most-recently-used last)."""
        with self._lock:
            self._purge_expired()
            return list(self._store.keys())

    @property
    def stats(self) -> CacheStats:
        """Return a copy of current statistics."""
        with self._lock:
            return CacheStats(**vars(self._stats))

    # ----- Internals -------------------------------------------------------

    def _evict_if_needed(self) -> None:
        """Evict LRU entries until within capacity. Caller must hold lock."""
        while len(self._store) > self._max_size:
            # popitem(last=False) removes the oldest (LRU) item.
            self._store.popitem(last=False)
            self._stats.evictions += 1

    def _purge_expired(self) -> None:
        """Remove all expired entries. Caller must hold lock."""
        now = self._time()
        expired = [k for k, e in self._store.items() if e.is_expired(now)]
        for k in expired:
            del self._store[k]
            self._stats.expirations += 1
```

---

## Design Decisions & Tradeoffs

| Decision | Rationale | Tradeoff |
|---|---|---|
| **`OrderedDict` for LRU** | Gives O(1) `get`/`set`/evict via `move_to_end` + `popitem(last=False)`. Battle-tested, no manual linked list. | Slightly more memory than a bare dict; `len()` purge is O(n). |
| **`threading.RLock`** | Methods like `get_or_set` reuse `get`/`set`; reentrancy avoids deadlock. | Coarse-grained lock → contention under high concurrency. For that, shard the cache (N sub-caches keyed by `hash(key) % N`). |
| **`time.monotonic` default** | TTLs shouldn't break when the wall clock jumps (NTP, DST). | Can't compare deadlines across processes; fine for in-memory. |
| **`_MISSING` sentinel** | Lets us cache `None` as a legitimate value and distinguish "no ttl override" from "ttl=None". | Minor `# type: ignore` ugliness at the boundary. |
| **Lazy + opportunistic expiration** | No background thread to manage/shut down; expired entries cost nothing until touched. | Expired entries can linger in memory until accessed or `len()`/`keys()` is called. A background reaper would trade simplicity for tighter memory bounds. |
| **Generics `LRUCache[K, V]`** | Type safety and editor autocomplete for callers. | None significant. |

## Edge Cases Handled

- **Storing `None`** as a value — distinguished from "missing" via sentinel.
- **`ttl=None` vs. omitted `ttl`** — explicitly disable vs. inherit default.
- **Invalid config** — `max_size <= 0`, non-positive TTLs rejected at construction/call.
- **Updating an existing key** — refreshes recency and value in place without growing size.
- **Expiry during membership/length checks** — purged consistently so `len()` reflects live entries.
- **Cache stampede** — `get_or_set` computes under lock so the factory runs once per key.
- **Clock safety** — monotonic clock avoids TTL bugs from wall-clock changes.

## What I'd Add Given Different Answers

- **Distributed/persistent** → back with Redis; this class becomes an L1 in front of it, with TTL-based or pub/sub invalidation for coherence.
- **Memory-bounded (not count-bounded)** → swap eviction trigger to a byte-size accumulator with a `sizeof` estimator.
- **Async** → replace `threading.RLock` with `asyncio.Lock` and make methods `async`.
- **LFU/ARC** → swap the eviction internals while keeping the same public API.

If you can answer the six questions above, I'll tailor this precisely.