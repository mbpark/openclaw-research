## Task 2.3: Priority Queue with Decrease-Key

**Description:**
Implement a priority queue that supports efficient decrease-key. A standard binary heap is O(n) for decrease-key and will be rejected.

### 2.3a: Basic Interface

**Part A - Core Operations:**
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

    def insert(self, key: int, value: T) -> None:
        """Insert key-value pair. O(1) target."""
        ...

    def extract_min(self) -> Optional[Tuple[int, T]]:
        """Extract and return (key, value) with lowest priority. O(?) target."""
        ...

    def size(self) -> int:
        """Return number of entries. O(1)."""
        ...
