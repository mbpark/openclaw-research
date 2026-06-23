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


class PriorityQueu