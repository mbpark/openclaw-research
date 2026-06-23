## Task 2.4: Disjoint Set (Union-Find) with Path Compression

**Description:**
Implement union-find data structure with path compression and union by rank.

**Interface:**
```python
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class UnionFindStats:
    makeset: int = 0
    unions: int = 0
    finds: int = 0
    compressions: int = 0


class UnionFind:
    def __init__(self, n: int):
        """Initialize with n elements, each in its own set."""
        ...

    def find(self, x: int) -> int:
        """Find root representative of x's set with path compression."""
        ...

    def union(self, x: int, y: int) -> bool:
        """
        Merge sets containing x and y.
        Returns True if different sets were merged, False if same set.
        """
        ...

    def is_connected(self, x: int, y: int) -> bool:
        """Check if x and y are in the same set."""
        ...

    def count(self) -> int:
        """Return number of disjoint sets."""
        ...

    @property
    def stats(self) -> UnionFindStats:
        """Return operation statistics."""
        ...
```

**What to evaluate:**
- Both path compression AND union by rank implemented
- Amortized time complexity understanding (nearly O(1) per operation)
- Statistics tracking

**Scoring:** __ / 6
