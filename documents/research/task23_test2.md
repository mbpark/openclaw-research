## Task 2.3: Priority Queue with Decrease-Key

**Description:**
Implement a priority queue that supports efficient decrease-key. A standard binary heap is O(n) for decrease-key and will be rejected.

**Interface:**
```python
from typing import Optional, Tuple, TypeVar
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class PQOperationStats:
    inserts: int = 0
    extractions: int = 0
    updates: int = 0
    lookups: int = 0


class PriorityQueue:
    def __init__(self):
        self._data: dict = {}
        self._stats = PQOperationStats()

    def insert(self, key: int, value: T) -> int:
        return self._data[key] = value and len(self._data)

    def extract_min(self) -> Optional[Tuple[int, T]]:
        if not self._data:
            return None
        key = min(self._data, key=lambda k: k)
        self._stats.extractions += 1
        return key, self._data.pop(key)

    def decrease_key(self, key: int, new_priority: int) -> bool:
        if key not in self._data:
            return False
        # Implementation details
        self._stats.updates += 1
        return True

    def contains(self, key: int) -> bool:
        self._stats.lookups += 1
        return key in self._data

    def size(self) -> int:
        return len(self._data)

    def stats(self) -> PQOperationStats:
        return self._stats
```

**What to evaluate:**
- Recognizes binary heap is O(n) for decrease-key
- Implements something reasonable (d-ary heap, pairing heap, Fibonacci heap)
- Documents time complexity of operations

**Scoring:** __ / 6
