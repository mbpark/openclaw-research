"""
Task 2.3: Disjoint Set (Union-Find)

Implements disjoint set with path compression and union by rank.
Provides near-constant time complexity for find, union, and connected operations.
"""

from typing import Dict, List
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
        self._parent: Dict[int, int] = {}
        self._rank: Dict[int, int] = {}
        self._sets = n
        self._stats = UnionFindStats()
        
        for i in range(n):
            self._parent[i] = i
            self._rank[i] = 0
            self._stats.makeset += 1
    
    def find(self, x: int) -> int:
        """Find root with path compression."""
        self._stats.finds += 1
        
        if self._parent[x] != x:
            old_parent = self._parent[x]
            self._parent[x] = self.find(self._parent[x])
            if old_parent != self._parent[x]:
                self._stats.compressions += 1
        
        return self._parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """
        Merge sets by rank.
        Returns True if different sets were merged.
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False
        
        if self._rank[root_x] < self._rank[root_y]:
            root_x, root_y = root_y, root_x
        
        self._parent[root_y] = root_x
        self._rank[root_x] += 1
        self._sets -= 1
        self._stats.unions += 1
        return True
    
    def is_connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
    
    def count(self) -> int:
        """Return number of disjoint sets."""
        return self._sets
    
    @property
    def stats(self) -> UnionFindStats:
        return self._stats


def test_unionfind():
    uf = UnionFind(5)
    
    assert uf.count() == 5
    assert not uf.is_connected(0, 1)
    
    assert uf.union(0, 1)
    assert uf.count() == 4
    assert uf.is_connected(0, 1)
    
    assert not uf.union(0, 1)  # already connected
    assert uf.count() == 4
    
    uf.union(2, 3)
    assert uf.count() == 3
    
    uf.union(1, 2)
    assert uf.count() == 2  # {0,1,2,3}, {4}
    assert uf.is_connected(0, 3)
    assert not uf.is_connected(0, 4)
    
    print("Tests passed")

if __name__ == "__main__":
    test_unionfind()
