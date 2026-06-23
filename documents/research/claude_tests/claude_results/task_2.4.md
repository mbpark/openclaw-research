# Disjoint Set (Union-Find) Implementation

## Complete Code

```python
from typing import List
from dataclasses import dataclass, field


@dataclass
class UnionFindStats:
    """Tracks operation statistics for the UnionFind structure.

    Attributes:
        makeset: Number of singleton sets created (initialization).
        unions: Number of successful merges (distinct sets joined).
        finds: Total number of find() calls (including recursive/internal).
        compressions: Number of parent-pointer rewrites during path compression.
    """
    makeset: int = 0
    unions: int = 0
    finds: int = 0
    compressions: int = 0


class UnionFind:
    """Disjoint Set (Union-Find) with path compression and union by rank.

    Provides near-constant amortized time per operation: the total cost of
    m operations on n elements is O(m * α(n)), where α is the inverse
    Ackermann function (effectively <= 4 for any practical input).

    Invariants:
        - Each element belongs to exactly one set.
        - Each set has a unique root (representative).
        - rank[root] is an upper bound on the height of the tree rooted there.
    """

    def __init__(self, n: int):
        """Initialize with n elements, each in its own singleton set.

        Args:
            n: Number of elements, labeled 0 .. n-1.

        Raises:
            ValueError: If n is negative.
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")

        self._parent: List[int] = list(range(n))
        self._rank: List[int] = [0] * n
        self._count: int = n
        self._stats = UnionFindStats(makeset=n)

    def _validate(self, x: int) -> None:
        """Bounds-check an element label.

        Args:
            x: Element label to validate.

        Raises:
            IndexError: If x is out of range [0, n).
        """
        if not (0 <= x < len(self._parent)):
            raise IndexError(
                f"element {x} out of range [0, {len(self._parent)})"
            )

    def find(self, x: int) -> int:
        """Find the root representative of x's set, with path compression.

        Uses iterative two-pass path compression: first walk to the root,
        then re-point every node on the path directly to the root. This
        avoids recursion-depth limits on deep (worst-case) trees.

        Args:
            x: Element to query.

        Returns:
            The root representative of the set containing x.

        Raises:
            IndexError: If x is out of range.
        """
        self._validate(x)
        self._stats.finds += 1

        # Pass 1: locate the root.
        root = x
        while self._parent[root] != root:
            root = self._parent[root]

        # Pass 2: compress the path so every node points directly to root.
        while self._parent[x] != root:
            next_node = self._parent[x]
            self._parent[x] = root
            self._stats.compressions += 1
            x = next_node

        return root

    def union(self, x: int, y: int) -> bool:
        """Merge the sets containing x and y, using union by rank.

        The root of the lower-rank tree is attached under the root of the
        higher-rank tree, keeping trees shallow. On a rank tie, one becomes
        the parent and its rank is incremented.

        Args:
            x: An element in the first set.
            y: An element in the second set.

        Returns:
            True if two distinct sets were merged; False if x and y were
            already in the same set.

        Raises:
            IndexError: If x or y is out of range.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already connected; no merge.

        # Union by rank: attach shorter tree under taller tree.
        if self._rank[root_x] < self._rank[root_y]:
            root_x, root_y = root_y, root_x  # Ensure root_x has >= rank.

        self._parent[root_y] = root_x
        if self._rank[root_x] == self._rank[root_y]:
            self._rank[root_x] += 1  # Height grows only on a tie.

        self._count -= 1
        self._stats.unions += 1
        return True

    def is_connected(self, x: int, y: int) -> bool:
        """Check whether x and y belong to the same set.

        Args:
            x: First element.
            y: Second element.

        Returns:
            True if x and y share a root representative.

        Raises:
            IndexError: If x or y is out of range.
        """
        return self.find(x) == self.find(y)

    def count(self) -> int:
        """Return the current number of disjoint sets.

        Returns:
            Number of distinct sets (starts at n, decreases by 1 per union).
        """
        return self._count

    @property
    def stats(self) -> UnionFindStats:
        """Return accumulated operation statistics.

        Returns:
            The live UnionFindStats instance for this structure.
        """
        return self._stats
```

## Demonstration / Quick Test

```python
if __name__ == "__main__":
    uf = UnionFind(10)
    assert uf.count() == 10

    assert uf.union(0, 1) is True
    assert uf.union(2, 3) is True
    assert uf.union(1, 3) is True          # merges {0,1} and {2,3}
    assert uf.union(0, 2) is False         # already connected

    assert uf.is_connected(0, 3) is True
    assert uf.is_connected(0, 4) is False
    assert uf.count() == 7                 # 10 - 3 successful unions

    print(uf.stats)
    # e.g. UnionFindStats(makeset=10, unions=3, finds=..., compressions=...)
```

## Design Decisions & Tradeoffs

**1. Iterative two-pass path compression (vs. recursion).**
The classic recursive `find` is elegant but risks `RecursionError` on adversarial inputs that build a long chain before any compression occurs (e.g. unioning in a degenerate order, though rank mitigates this). The iterative version walks to the root, then re-points each node. This keeps memory bounded and gives a clean place to increment `compressions` only when a pointer actually changes.

**2. Union by rank (vs. union by size).**
Both bound tree height to O(log n) *before* compression, and combined with compression both give O(α(n)) amortized. I chose rank because the prompt explicitly names it. Rank is an *upper bound* on height (not exact, since compression flattens trees without updating rank downward) — that's fine, it only needs to be a consistent comparison key.

**3. Combined complexity.** Path compression alone gives O(log n) amortized; union by rank alone gives O(log n) worst case. **Together** they yield O(α(n)) amortized — effectively constant. Using only one would be a correctness-passing but suboptimal answer.

**4. Statistics as a live mutable dataclass.** `stats` returns the internal instance rather than a copy. This is cheap and lets callers observe counters as they accumulate. Tradeoff: a caller could mutate it. If immutability mattered I'd return `dataclasses.replace(self._stats)` (a copy). I defined `finds` to count *every* `find` call (including the two inside each `union`), which makes the relationship `finds >= 2 * unions` observable.

## Edge Case Handling

| Case | Behavior |
|------|----------|
| `n = 0` | Valid empty structure; `count() == 0`, all lists empty. |
| `n < 0` | Raises `ValueError`. |
| Out-of-range element | `find`/`union`/`is_connected` raise `IndexError` via `_validate`. |
| `union(x, x)` (self) | `find(x) == find(x)`, returns `False`, no state change. |
| Repeated union of connected elements | Returns `False`, `unions` not incremented, `count` unchanged. |
| `is_connected(x, x)` | Returns `True` trivially. |
| Already-compressed paths | `find` does zero `compressions` increments (pass-2 loop exits immediately). |

---

## Re: Checkpoint 1 (Meta-feedback on the challenge design)

**Is the difficulty appropriate?** Yes — this is a solid mid-level bar. It separates candidates who know the textbook structure from those who implement *both* optimizations correctly and understand *why* α(n) emerges only from their combination. The statistics requirement adds a nice "read the spec carefully" dimension.

**Categories to drop/add?** Consider adding:
- **Connected-components enumeration** (`groups() -> List[List[int]]`) to test grouping logic.
- A **rollback / undo** variant (union-find without path compression, persistent) as a harder tier — this directly bridges into your *Category 3: Systems Design* (e.g., snapshotting state for transactional rollback).

**Scoring granularity?** The current `/6` is coarse for 4 evaluation points. I'd suggest an explicit rubric:
- Path compression correct: 1
- Union by rank correct: 1
- Both combined (not just one): 1
- Stats accurate & complete: 1
- Edge cases (bounds, self-union, n=0): 1
- Complexity explanation / API correctness: 1

This makes partial credit reproducible across graders.

**Decision:** ☑ **Continue** (with optional rubric refinement above).

Would you like me to extend this into the systems-design framing — e.g., a thread-safe or persistent/rollbackable variant suitable for a transactional context?