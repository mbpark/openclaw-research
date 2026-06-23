# Union-Find Implementation

```python
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class UnionFindStats:
    """Tracks the number of operations performed on the structure.

    Attributes:
        makeset: Number of singleton sets created (at init / via add).
        unions: Number of successful merges (distinct sets joined).
        finds: Number of top-level find() invocations.
        compressions: Number of parent-pointer rewrites done by path compression.
    """
    makeset: int = 0
    unions: int = 0
    finds: int = 0
    compressions: int = 0


class UnionFind:
    """Disjoint Set Union (DSU) with path compression and union by rank.

    Path compression flattens the tree during find(), and union by rank
    keeps trees shallow by attaching the shorter tree under the taller one.
    Together they give an amortized cost of O(alpha(n)) per operation,
    where alpha is the inverse Ackermann function (effectively constant).

    Example:
        >>> uf = UnionFind(5)
        >>> uf.union(0, 1)
        True
        >>> uf.union(1, 2)
        True
        >>> uf.is_connected(0, 2)
        True
        >>> uf.count()
        3
    """

    def __init__(self, n: int) -> None:
        """Initialize with n elements (0..n-1), each in its own set.

        Args:
            n: Number of elements. Must be non-negative.

        Raises:
            ValueError: If n is negative.
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")

        self._parent: List[int] = list(range(n))
        # Rank is an upper bound on tree height (not exact due to compression).
        self._rank: List[int] = [0] * n
        self._num_sets: int = n
        self._stats = UnionFindStats(makeset=n)

    def _validate(self, x: int) -> None:
        """Ensure x is a valid element index.

        Args:
            x: Element to validate.

        Raises:
            IndexError: If x is out of the valid range.
        """
        if not (0 <= x < len(self._parent)):
            raise IndexError(
                f"element {x} out of range [0, {len(self._parent)})"
            )

    def find(self, x: int) -> int:
        """Find root representative of x's set with path compression.

        Uses iterative two-pass path compression: first walk to the root,
        then point every node along the path directly at the root. The
        iterative approach avoids recursion-depth limits on degenerate trees.

        Args:
            x: Element whose set representative is sought.

        Returns:
            The root element identifying x's set.

        Raises:
            IndexError: If x is out of range.
        """
        self._validate(x)
        self._stats.finds += 1

        # Pass 1: locate the root.
        root = x
        while self._parent[root] != root:
            root = self._parent[root]

        # Pass 2: compress the path so each node points to the root.
        while self._parent[x] != root:
            next_node = self._parent[x]
            self._parent[x] = root
            self._stats.compressions += 1
            x = next_node

        return root

    def union(self, x: int, y: int) -> bool:
        """Merge sets containing x and y using union by rank.

        Args:
            x: First element.
            y: Second element.

        Returns:
            True if two distinct sets were merged, False if x and y were
            already in the same set.

        Raises:
            IndexError: If x or y is out of range.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already connected; no merge performed.

        # Attach the lower-rank tree under the higher-rank root.
        if self._rank[root_x] < self._rank[root_y]:
            root_x, root_y = root_y, root_x  # Ensure root_x has >= rank.

        self._parent[root_y] = root_x
        # Equal ranks: the resulting tree grows by one level.
        if self._rank[root_x] == self._rank[root_y]:
            self._rank[root_x] += 1

        self._num_sets -= 1
        self._stats.unions += 1
        return True

    def is_connected(self, x: int, y: int) -> bool:
        """Check if x and y belong to the same set.

        Args:
            x: First element.
            y: Second element.

        Returns:
            True if x and y share a root, else False.

        Raises:
            IndexError: If x or y is out of range.
        """
        return self.find(x) == self.find(y)

    def count(self) -> int:
        """Return the current number of disjoint sets.

        Returns:
            Count of distinct sets (maintained in O(1)).
        """
        return self._num_sets

    @property
    def stats(self) -> UnionFindStats:
        """Return accumulated operation statistics.

        Returns:
            The internal UnionFindStats record.
        """
        return self._stats
```

## Design Decisions & Tradeoffs

**1. Iterative path compression (two-pass)**
I chose an iterative `find` over the elegant recursive one-liner (`parent[x] = find(parent[x])`). On adversarial inputs a long chain can be built before any compression occurs, and recursion would risk a `RecursionError` / stack overflow. The two-pass approach is stack-safe for arbitrarily large structures. The tradeoff is two traversals of the path instead of one, but both are O(path length) and the constant factor is negligible.

**2. Union by rank vs. union by size**
I used **rank** (height upper bound) as specified. Rank is cheaper to maintain (only increments on ties) but, unlike size, can't answer "how big is this set?" If the API needed set sizes, union by size would be preferable since both give the same O(alpha(n)) guarantee.

**3. Combining the two heuristics**
Path compression alone gives O(log n) amortized; union by rank alone gives O(log n) worst case. Together they yield O(alpha(n)) amortized — effectively constant for all practical n (alpha(n) ≤ 4 for n < 2^65536).

**4. O(1) `count()`**
Rather than recomputing roots, I decrement `_num_sets` on each successful union. This keeps `count()` constant-time at the cost of one integer maintained during unions.

**5. Statistics semantics**
- `finds` counts top-level `find` calls (so `union` contributes 2, `is_connected` 2).
- `compressions` counts individual parent-pointer rewrites, giving a fine-grained measure of compression work.
- `unions` counts only *successful* merges, matching the boolean return contract.
- `makeset` is seeded at construction.

A reasonable alternative would be to *not* count internal finds triggered by `union`. I chose to count them because they reflect real work and make the stats auditable.

## Edge Case Handling

| Case | Behavior |
|------|----------|
| `n == 0` | Empty structure; `count() == 0`, any `find` raises `IndexError`. |
| `n < 0` | `ValueError` at construction. |
| Out-of-range element | `IndexError` via `_validate`. |
| `union(x, x)` (self-union) | Returns `False`, no merge, but still records 2 finds. |
| Already-connected union | Returns `False`, `_num_sets` unchanged. |
| Repeated `find` on same chain | First call compresses; later calls are O(1). |
| Degenerate deep chain | Iterative find avoids recursion limits. |

---

## Re: Checkpoint 1 — Calibration Feedback

**Difficulty:** Appropriate for a mid-level/senior screen. The task is well-bounded but discriminating: weak candidates implement only path compression *or* only union by rank; strong ones do both correctly and can articulate the inverse-Ackermann bound.

**Categories:** The current rubric (both heuristics + complexity understanding + stats) is solid. I'd suggest one refinement:
- **Add** an explicit "robustness/edge cases" sub-criterion — recursion safety and input validation separate good from great answers and are currently implicit.
- **Consider dropping** stats-tracking weight slightly; it's largely bookkeeping and doesn't test core DSU insight.

**Scoring granularity:** 6 points is a bit coarse for the spread of behaviors. I'd recommend a half-point scale or splitting into:
1. Path compression correct (1)
2. Union by rank correct (1)
3. `union` return-value / `count` correctness (1)
4. Complexity articulation (1)
5. Stats tracking (1)
6. Edge cases & robustness (1)

**Decision:** ☑ **Adjust** — keep the task, add the robustness criterion, and move to half-point granularity.

Ready to proceed to **Category 3: Systems Design** when you are.