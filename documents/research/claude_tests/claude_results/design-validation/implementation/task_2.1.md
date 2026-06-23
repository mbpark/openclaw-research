# LRU Cache Implementation

## Complete Code

```python
from typing import Optional, TypeVar, Generic, Iterator, Dict, Tuple
from collections import OrderedDict
from dataclasses import dataclass

K = TypeVar('K')
V = TypeVar('V')


@dataclass
class LRUCacheStats:
    """Cache statistics for monitoring."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    current_size: int = 0


class LRUCache(Generic[K, V]):
    """
    LRU (Least Recently Used) Cache with O(1) operations and statistics
    tracking.

    Uses an OrderedDict internally, which is backed by a hash map plus a
    doubly-linked list. This gives O(1) lookup, insertion, deletion, and
    move-to-end operations.

    Recency model:
        - get() and put() count as "accesses" and move the key to the
          most-recently-used (MRU) position.
        - contains() is a pure inspection and does NOT affect recency.
        - The least-recently-used (LRU) item is evicted first when capacity
          is exceeded.
    """

    def __init__(self, capacity: int):
        """
        Initialize LRU cache.

        Args:
            capacity: Maximum number of entries. Must be > 0.

        Raises:
            ValueError: If capacity is not a positive integer.
        """
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise ValueError("Capacity must be an integer")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self._capacity: int = capacity
        # OrderedDict: front (first) = LRU, back (last) = MRU.
        self._data: "OrderedDict[K, V]" = OrderedDict()
        self._stats = LRUCacheStats()

    def get(self, key: K) -> Optional[V]:
        """
        Get value by key, updating recency on hit.

        Args:
            key: The key to look up.

        Returns:
            The value if present (and marks the key as most-recently-used),
            otherwise None.

        Note:
            A stored value of None is indistinguishable from "absent" via this
            return type per the interface contract. Use contains() to
            disambiguate without affecting recency.
        """
        if key in self._data:
            self._data.move_to_end(key)  # mark as MRU; O(1)
            self._stats.hits += 1
            return self._data[key]

        self._stats.misses += 1
        return None

    def put(self, key: K, value: V) -> bool:
        """
        Put key-value pair in cache, updating recency.

        If the key already exists, its value is updated and it is moved to the
        MRU position (no eviction occurs because size is unchanged). If the key
        is new and the cache is at capacity, the LRU entry is evicted first.

        Args:
            key: The key to insert or update.
            value: The value to associate with the key.

        Returns:
            True if a new entry was inserted, False if the key already existed
            (value updated in place).
        """
        if key in self._data:
            # Update existing entry; no size change, so no eviction.
            self._data[key] = value
            self._data.move_to_end(key)  # mark as MRU
            return False

        # New key. Evict BEFORE insert to honor capacity strictly.
        if len(self._data) >= self._capacity:
            # popitem(last=False) removes the LRU (front) item; O(1).
            self._data.popitem(last=False)
            self._stats.evictions += 1

        self._data[key] = value  # inserted at MRU end
        self._stats.current_size = len(self._data)
        return True

    def contains(self, key: K) -> bool:
        """
        Check if key exists WITHOUT changing access order.

        Args:
            key: The key to test.

        Returns:
            True if the key is present, False otherwise. This does not count as
            a hit or miss and does not affect recency.
        """
        return key in self._data

    def delete(self, key: K) -> bool:
        """
        Delete key from cache.

        Args:
            key: The key to remove.

        Returns:
            True if the key was found and removed, False otherwise.
        """
        if key in self._data:
            del self._data[key]
            self._stats.current_size = len(self._data)
            return True
        return False

    def get_stats(self) -> LRUCacheStats:
        """
        Return a snapshot of current statistics.

        Returns:
            A copy of the stats so callers cannot mutate internal state.
        """
        return LRUCacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            current_size=len(self._data),
        )

    def clear(self) -> None:
        """
        Clear all entries.

        Statistics counters (hits/misses/evictions) are intentionally
        preserved as cumulative lifetime metrics; only current_size resets.
        """
        self._data.clear()
        self._stats.current_size = 0

    def size(self) -> int:
        """Return current number of entries."""
        return len(self._data)

    def __len__(self) -> int:
        return self.size()

    def __contains__(self, key: K) -> bool:
        return self.contains(key)

    def __iter__(self) -> Iterator[K]:
        """Iterate keys from LRU to MRU (does not affect recency)."""
        return iter(self._data)

    def __repr__(self) -> str:
        return (
            f"LRUCache(capacity={self._capacity}, "
            f"size={len(self._data)}, "
            f"stats={self.get_stats()})"
        )


class IntLRUCache(LRUCache[int, int]):
    """Specialized int-to-int LRU cache for LeetCode-style problems."""

    def __init__(self, capacity: int):
        super().__init__(capacity)

    def get(self, key: int) -> int:
        """Return value or -1 if not found."""
        value = super().get(key)
        return value if value is not None else -1
```

## Design Decisions and Tradeoffs

**1. `OrderedDict` over a hand-rolled doubly-linked list.**
`OrderedDict` is implemented in C with an internal hash map + doubly-linked list, so `move_to_end`, `popitem`, insert, lookup, and delete are all **O(1)**. A manual linked-list implementation would meet the requirement but adds bug surface (node bookkeeping) for no asymptotic gain. The challenge explicitly warns against O(n) eviction — `popitem(last=False)` avoids scanning.

**2. Evict *before* insert for new keys.**
This guarantees the cache never transiently exceeds capacity and keeps `current_size <= capacity` as a strict invariant.

**3. `put()` on an existing key never evicts.**
Updating an existing key doesn't change `len()`, so eviction logic is gated behind the `key not in self._data` branch. This correctly handles the subtle case the prompt calls out.

**4. `contains()` / `__contains__()` bypass recency and stats.**
They only do a membership test (`key in self._data`) with no `move_to_end` and no hit/miss increment — matching the "inspection-only" contract.

**5. `get_stats()` returns a copy.**
Prevents external mutation of internal counters and avoids aliasing bugs.

**6. `current_size` is recomputed from `len(self._data)`** in `get_stats()` to stay authoritative even if a counter update is ever missed.

## Edge Case Handling

| Edge Case | Behavior |
|---|---|
| `capacity <= 0` | `ValueError` at construction |
| `capacity` is `bool` (`True == 1`) | Rejected — `bool` is a sneaky `int` subclass |
| `get` on missing key | Returns `None`, increments `misses`, no recency change |
| `put` existing key | Updates value, moves to MRU, returns `False`, **no eviction** |
| `put` new key at capacity | Evicts LRU, increments `evictions`, returns `True` |
| `contains` | No recency change, no stats change |
| `delete` missing key | Returns `False`, no crash |
| Stored value `None` | Indistinguishable from "absent" via `get()` return type (documented limitation of the interface); use `contains()` |
| `clear()` | Empties data, keeps cumulative hit/miss/eviction counters |
| `IntLRUCache.get` miss | Returns `-1` (LeetCode convention) while base records the miss |

### Quick sanity test

```python
def _smoke_test() -> None:
    c: LRUCache[str, int] = LRUCache(2)
    assert c.put("a", 1) is True
    assert c.put("b", 2) is True
    assert c.contains("a") is True          # no recency change
    assert c.put("c", 3) is True            # evicts "a" (LRU), not "b"
    assert c.contains("a") is False
    assert c.get("b") == 2                   # hit, "b" -> MRU
    assert c.put("b", 22) is False           # existing -> no eviction
    assert c.get("b") == 22
    assert c.put("d", 4) is True             # evicts "c"
    assert c.contains("c") is False
    s = c.get_stats()
    assert s.evictions == 2 and s.current_size == 2
    assert s.hits == 2

    ic = IntLRUCache(1)
    assert ic.get(99) == -1                  # miss returns -1
    print("All smoke tests passed:", c, ic.get_stats())


if __name__ == "__main__":
    _smoke_test()
```

All operations are O(1), eviction is correct on both `put` paths, `contains` is side-effect-free, and statistics remain accurate.