# LRU Cache Implementation

## Complete Code

```python
from typing import Optional, TypeVar, Generic, Iterator, Tuple
from collections import OrderedDict
from dataclasses import dataclass

K = TypeVar('K')
V = TypeVar('V')


@dataclass
class LRUCacheStats:
    """Cache statistics for monitoring.

    Attributes:
        hits: Number of successful ``get`` lookups.
        misses: Number of failed ``get`` lookups.
        evictions: Number of entries removed due to capacity overflow.
        current_size: Current number of entries in the cache.
    """
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    current_size: int = 0


class LRUCache(Generic[K, V]):
    """LRU (Least Recently Used) Cache with O(1) operations.

    Backed by :class:`collections.OrderedDict`, which maintains insertion
    order and supports O(1) move-to-end and pop-from-front operations.

    Recency convention: the *most* recently used item is at the *end* of the
    underlying ordered dict; the *least* recently used item is at the *front*.
    """

    def __init__(self, capacity: int):
        """Initialize the LRU cache.

        Args:
            capacity: Maximum number of entries. Must be a positive integer.

        Raises:
            ValueError: If ``capacity`` is not positive.
            TypeError: If ``capacity`` is not an integer (and not a bool-free int).
        """
        # bool is a subclass of int; reject it explicitly to avoid
        # silently accepting True (==1) / False (==0).
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("Capacity must be an integer")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self._capacity: int = capacity
        self._data: "OrderedDict[K, V]" = OrderedDict()
        self._stats = LRUCacheStats()

    def get(self, key: K) -> Optional[V]:
        """Get value by key, updating recency on a hit.

        Args:
            key: The key to look up.

        Returns:
            The value if present (and marks it most-recently-used),
            otherwise ``None``.

        Note:
            A stored value of ``None`` is indistinguishable from a miss in the
            return value, but statistics are still recorded as a hit. Use
            :meth:`contains` if you need to distinguish "absent" from
            "present with value None".
        """
        if key in self._data:
            self._data.move_to_end(key)  # O(1): mark as most recently used
            self._stats.hits += 1
            return self._data[key]
        self._stats.misses += 1
        return None

    def put(self, key: K, value: V) -> bool:
        """Put a key-value pair into the cache.

        If the key already exists, its value is updated and it is marked as
        most recently used (no eviction occurs, since size is unchanged).

        If the key is new and the cache is at capacity, the least recently
        used entry is evicted first.

        Args:
            key: The key to insert or update.
            value: The value to associate with ``key``.

        Returns:
            ``True`` if a new entry was inserted,
            ``False`` if an existing key was updated.
        """
        if key in self._data:
            # Update existing entry: refresh value and recency. No eviction.
            self._data[key] = value
            self._data.move_to_end(key)
            return False

        # New key: evict LRU first if we're at capacity.
        # Capacity is always >= 1, so this evicts at most one entry.
        if len(self._data) >= self._capacity:
            self._data.popitem(last=False)  # O(1): pop least recently used
            self._stats.evictions += 1

        self._data[key] = value
        self._stats.current_size = len(self._data)
        return True

    def contains(self, key: K) -> bool:
        """Check if a key exists WITHOUT changing access order.

        Args:
            key: The key to check.

        Returns:
            ``True`` if the key is present, ``False`` otherwise.

        Note:
            This does not count as a hit or miss in statistics, and does not
            touch recency ordering.
        """
        return key in self._data

    def delete(self, key: K) -> bool:
        """Delete a key from the cache.

        Args:
            key: The key to remove.

        Returns:
            ``True`` if the key was found and removed, ``False`` otherwise.
        """
        if key in self._data:
            del self._data[key]
            self._stats.current_size = len(self._data)
            return True
        return False

    def get_stats(self) -> LRUCacheStats:
        """Return a snapshot copy of current statistics.

        Returns:
            A new :class:`LRUCacheStats` instance so callers cannot mutate
            internal state. ``current_size`` is always refreshed to the true
            size.
        """
        return LRUCacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            current_size=len(self._data),
        )

    def clear(self) -> None:
        """Clear all entries.

        Statistics counters (hits/misses/evictions) are preserved; only the
        stored entries and ``current_size`` are reset. This keeps lifetime
        monitoring counters intact.
        """
        self._data.clear()
        self._stats.current_size = 0

    def size(self) -> int:
        """Return the current number of entries."""
        return len(self._data)

    @property
    def capacity(self) -> int:
        """Return the configured maximum capacity."""
        return self._capacity

    def __len__(self) -> int:
        return self.size()

    def __contains__(self, key: K) -> bool:
        return self.contains(key)

    def __iter__(self) -> Iterator[K]:
        """Iterate over keys from least to most recently used."""
        return iter(self._data)

    def items(self) -> Iterator[Tuple[K, V]]:
        """Iterate over (key, value) pairs, least to most recently used."""
        return iter(self._data.items())

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
        """Return value or -1 if not found.

        Returns:
            The integer value, or ``-1`` if the key is absent.

        Note:
            If a value of ``-1`` was stored, the return value is ambiguous
            (same as a miss) — this matches LeetCode conventions where ``-1``
            is the sentinel for "not found".
        """
        value = super().get(key)
        return value if value is not None else -1
```

## Design Decisions & Tradeoffs

### Why `OrderedDict`?
`OrderedDict` gives **O(1)** for all required operations:
- `move_to_end(key)` — refresh recency on hit/update
- `popitem(last=False)` — evict LRU from the front
- `del` / `in` / index — standard dict O(1)

The hand-rolled alternative (doubly-linked list + hash map) is the classic interview answer, but it's more error-prone (pointer bugs) with no asymptotic benefit. `OrderedDict` is itself implemented as a hash map + doubly-linked list in CPython, so we get the textbook structure for free.

### Recency convention
End = most recently used, front = least recently used. This makes eviction a single `popitem(last=False)`.

### Statistics correctness
- `get` records exactly one hit **or** one miss per call.
- `put` is **not** counted as a hit/miss — it's a write, not a lookup. This is the standard convention; conflating the two skews hit-rate metrics.
- `contains` deliberately records nothing and touches no ordering — it's a pure inspection.
- `get_stats()` returns a **copy** so external code can't corrupt internal counters, and refreshes `current_size` defensively.

## Edge Case Handling

| Edge case | Behavior |
|-----------|----------|
| `capacity <= 0` | `ValueError` at construction |
| `capacity` is `bool` / non-int | `TypeError` (since `True == 1` would silently pass `isinstance(int)`) |
| `put` on existing key | Updates value + recency, returns `False`, **no eviction** (size unchanged) |
| `put` new key when full | Evicts exactly one LRU entry, increments `evictions` |
| `capacity == 1` | Each new distinct key evicts the previous one; works correctly |
| `get` on missing key | Returns `None`, increments `misses`, no ordering change |
| Storing `None` as value | `get` returns `None` (ambiguous with miss) but stats record a hit; use `contains` to disambiguate — **documented** |
| `delete` missing key | Returns `False`, no error |
| `clear` | Resets entries + size; **preserves** lifetime hit/miss/eviction counters |
| `IntLRUCache` miss | Returns `-1` per LeetCode convention |

### Key subtlety: update-vs-insert eviction
The critical bug most implementations make is evicting on **every** `put`. Here, eviction only happens in the `new key + at capacity` branch. Updating an existing key short-circuits *before* the capacity check, so size never overflows and no spurious eviction occurs. Verified by:

```python
c = LRUCache[str, int](2)
c.put("a", 1); c.put("b", 2)
c.put("a", 10)              # update, not insert
assert c.size() == 2
assert c.get_stats().evictions == 0
assert c.get("a") == 10
```