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
    LRU (Least Recently Used) Cache with O(1) operations and statistics.

    Backed by an OrderedDict, which maintains insertion/access order via an
    internal doubly-linked list + hash map, giving O(1) lookup, insertion,
    deletion, and move-to-end operations.

    Ordering convention:
        - The *most recently used* (MRU) item is at the END of the OrderedDict.
        - The *least recently used* (LRU) item is at the FRONT.
        - Eviction removes from the front (popitem(last=False)).
    """

    def __init__(self, capacity: int):
        """
        Initialize LRU cache.

        Args:
            capacity: Maximum number of entries. Must be > 0.

        Raises:
            ValueError: If capacity is not a positive integer.
        """
        if not isinstance(capacity, int):
            raise ValueError("Capacity must be an integer")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity: int = capacity
        self._data: "OrderedDict[K, V]" = OrderedDict()
        self._stats = LRUCacheStats()

    def get(self, key: K) -> Optional[V]:
        """
        Get value by key, marking it as most recently used.

        Args:
            key: The key to look up.

        Returns:
            The value if present (and updates recency), None otherwise.

        Note:
            If a stored value is literally None, this method cannot distinguish
            "present with None value" from "absent" via the return value alone.
            Use `contains()` for a definitive presence check. Statistics are
            still tracked correctly regardless.
        """
        if key in self._data:
            self._data.move_to_end(key)  # mark as MRU; O(1)
            self._stats.hits += 1
            return self._data[key]
        self._stats.misses += 1
        return None

    def put(self, key: K, value: V) -> bool:
        """
        Put a key-value pair in the cache, marking it as most recently used.

        If the key already exists, its value is updated and recency refreshed
        (no eviction occurs because size does not grow). If the key is new and
        the cache is full, the least recently used entry is evicted first.

        Args:
            key: The key to insert/update.
            value: The value to associate with the key.

        Returns:
            True if a new entry was inserted, False if the key already existed.
        """
        if key in self._data:
            # Update existing entry; refresh recency. No size change, no eviction.
            self._data[key] = value
            self._data.move_to_end(key)
            return False

        # New key. Evict BEFORE insertion if at capacity to maintain invariant.
        if len(self._data) >= self._capacity:
            # popitem(last=False) removes the LRU (front) item in O(1).
            self._data.popitem(last=False)
            self._stats.evictions += 1

        self._data[key] = value  # inserted at end => MRU
        self._stats.current_size = len(self._data)
        return True

    def contains(self, key: K) -> bool:
        """
        Check if a key exists WITHOUT changing access order or statistics.

        Args:
            key: The key to check.

        Returns:
            True if the key is present, False otherwise.
        """
        return key in self._data  # pure dict membership; does not reorder

    def delete(self, key: K) -> bool:
        """
        Delete a key from the cache.

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
            A copy of the internal stats so external mutation cannot corrupt
            the cache's accounting.
        """
        return LRUCacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            current_size=len(self._data),
        )

    def clear(self) -> None:
        """Clear all entries. Does NOT reset cumulative hit/miss/eviction counts."""
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
        """Iterate keys from LRU (front) to MRU (end). Does not affect ordering."""
        return iter(self._data)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(capacity={self._capacity}, "
            f"size={len(self._data)})"
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

## Design Decisions & Tradeoffs

### 1. `OrderedDict` over a hand-rolled doubly-linked list
`OrderedDict` already provides exactly the primitives we need, all O(1):
- `move_to_end(key)` — promote to MRU
- `popitem(last=False)` — evict LRU
- `in` / `del` — membership / removal

A manual doubly-linked-list + dict implementation would give the same complexity but with more code and more chances for bugs (broken pointer relinking on delete). The tradeoff: `OrderedDict` carries slightly more memory overhead per node, but correctness and clarity win.

### 2. Ordering convention — MRU at the end
`move_to_end` defaults to moving to the end, and inserting a new key also lands at the end, so "end = most recent" is the natural, consistent convention. Eviction therefore pops from the **front** (`last=False`).

### 3. Eviction order in `put`
Eviction happens **before** insertion of a new key. This guarantees we never momentarily exceed capacity, and we never accidentally evict the key we just inserted.

### 4. `put` on an existing key never evicts
This is a common bug. Updating an existing key does **not** grow the size, so no eviction should occur. The implementation explicitly branches: existing key → update + `move_to_end`, return `False`; new key → maybe evict, insert, return `True`.

### 5. `contains` is side-effect free
It uses raw dict membership (`key in self._data`) and intentionally does **not** call `move_to_end` or touch stats. This is required by the spec and distinguishes "peeking" from "accessing".

### 6. `get_stats` returns a copy
Returning the live `_stats` object would let callers mutate internal counters. We return a fresh `LRUCacheStats` snapshot. `current_size` is recomputed from `len(self._data)` to guarantee it's always truthful even if some code path forgot to update it.

### 7. `clear` preserves cumulative counters
Hits/misses/evictions are cumulative monitoring metrics. Clearing the *data* shouldn't erase the operational history; only `current_size` resets. (This is a judgment call — documented explicitly so behavior is unambiguous.)

## Edge Case Handling

| Edge case | Behavior |
|---|---|
| `capacity <= 0` or non-int | `ValueError` at construction |
| `capacity == 1` | Works; each new key evicts the previous one |
| `put` existing key when full | Updates value, refreshes recency, **no eviction** |
| `put` new key when full | Evicts true LRU first, then inserts |
| `get` on missing key | Returns `None`, increments `misses`, order unchanged |
| `get` on present key | Returns value, increments `hits`, promotes to MRU |
| `contains` / `__contains__` | No recency change, no stat change |
| `delete` missing key | Returns `False`, no error |
| Stored value is literally `None` | `get` returns `None` ambiguously — documented; use `contains` for definitive check |
| `IntLRUCache.get` miss | Returns `-1` per LeetCode convention |
| External mutation of stats | Prevented — `get_stats` returns a copy |

### Quick sanity test

```python
def _demo() -> None:
    c: LRUCache[str, int] = LRUCache(2)
    assert c.put("a", 1) is True
    assert c.put("b", 2) is True
    assert "a" in c                  # contains: no reorder; "a" still LRU
    assert c.put("c", 3) is True     # evicts "a"
    assert c.get("a") is None        # miss
    assert c.put("b", 20) is False   # existing key: update, no eviction
    assert c.get("b") == 20          # hit, "b" now MRU
    assert c.put("d", 4) is True     # evicts "c" (LRU), not "b"
    assert c.get("c") is None
    assert c.get("b") == 20
    s = c.get_stats()
    assert s.evictions == 2 and s.current_size == 2

    ic = IntLRUCache(1)
    assert ic.get(99) == -1
    ic.put(1, 100)
    assert ic.get(1) == 100
    ic.put(2, 200)                   # evicts key 1
    assert ic.get(1) == -1

    try:
        LRUCache(0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    print("All checks passed.")


if __name__ == "__main__":
    _demo()
```

All operations are **O(1)** (amortized for the dict ops), the eviction-on-update bug is avoided, `contains` is side-effect free, capacity is validated, and statistics are accurate and tamper-resistant.