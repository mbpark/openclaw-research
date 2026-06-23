# Priority Queue with Decrease-Key

I'll implement two solutions: a **D-ary heap with index map** (pragmatic, cache-friendly) and a **Pairing heap** (elegant, amortized-optimal). The D-ary heap is my primary recommendation for most real-world use.

## Design Decision Summary

The core challenge is that a standard binary heap doesn't know *where* a key lives in the array, forcing an O(n) scan during `decrease_key`. The fix is an **auxiliary hash map** (`key → array index`) maintained on every swap. This gives O(1) lookup, making `decrease_key` O(log_d n) (just a sift-up).

---

## Primary Implementation: D-ary Heap

```python
from __future__ import annotations

from typing import Optional, Tuple, TypeVar, Generic, List, Dict
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class PQOperationStats:
    """Tracks counts of priority-queue operations for instrumentation/testing."""
    inserts: int = 0
    extractions: int = 0
    updates: int = 0
    lookups: int = 0


class PriorityQueue(Generic[T]):
    """
    Abstract-ish base defining the interface. The base methods raise
    NotImplementedError so misuse is caught early; concrete subclasses
    override them.
    """

    def __init__(self) -> None:
        self._stats = PQOperationStats()

    def insert(self, key: int, value: T) -> None:
        raise NotImplementedError

    def extract_min(self) -> Optional[Tuple[int, T]]:
        raise NotImplementedError

    def decrease_key(self, key: int, new_priority: int) -> bool:
        raise NotImplementedError

    def increase_key(self, key: int, new_priority: int) -> bool:
        raise NotImplementedError

    def contains(self, key: int) -> bool:
        raise NotImplementedError

    def peek(self) -> Optional[Tuple[int, T]]:
        raise NotImplementedError

    def delete(self, key: int) -> bool:
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError

    def stats(self) -> PQOperationStats:
        return self._stats


class _Node(Generic[T]):
    """
    A heap node. `priority` is the ordering value (lower = higher priority).
    `key` is a unique identifier used by the index map.
    `value` is the payload.
    """
    __slots__ = ("key", "priority", "value")

    def __init__(self, key: int, priority: int, value: T) -> None:
        self.key = key
        self.priority = priority
        self.value = value


class DaryHeapPriorityQueue(PriorityQueue[T]):
    """
    D-ary heap implementation with a hash index for O(1) key lookup.

    The key insight: a plain binary/d-ary heap cannot locate an arbitrary
    key in better than O(n). We maintain a side table `_index: key -> array
    position`, updated on every swap. This makes decrease_key a pure sift-up,
    i.e. O(log_d n).

    Time Complexity (n = #entries, d = branching factor):
    - insert:        O(log_d n)         -- one sift-up
    - extract_min:   O(d * log_d n)     -- sift-down compares d children/level
    - peek:          O(1)
    - decrease_key:  O(log_d n)         -- sift-up only
    - increase_key:  O(d * log_d n)     -- sift-down only
    - delete:        O(d * log_d n)     -- replace + sift either direction
    - contains:      O(1)
    - size:          O(1)

    Space: O(n) for the array + O(n) for the index map.

    Choice of d:
    - d=2 is the classic binary heap.
    - Larger d -> shallower tree -> faster decrease_key/insert (fewer levels),
      but slower extract_min (more children scanned per level). d=4 is a common
      sweet spot for decrease-key-heavy workloads like Dijkstra.
    """

    def __init__(self, d: int = 4) -> None:
        """
        Args:
            d: Branching factor (>= 2).
        """
        super().__init__()
        if d < 2:
            raise ValueError("Branching factor d must be >= 2")
        self._d = d
        self._heap: List[_Node[T]] = []
        self._index: Dict[int, int] = {}  # key -> position in self._heap

    # ----- internal helpers ------------------------------------------------

    def _parent(self, i: int) -> int:
        return (i - 1) // self._d

    def _child(self, i: int, c: int) -> int:
        """Index of the c-th child (0-based) of node at position i."""
        return self._d * i + c + 1

    def _swap(self, i: int, j: int) -> None:
        """Swap two heap positions AND keep the index map consistent."""
        hi, hj = self._heap[i], self._heap[j]
        self._heap[i], self._heap[j] = hj, hi
        self._index[hi.key] = j
        self._index[hj.key] = i

    def _sift_up(self, i: int) -> None:
        """Move node at i toward the root while it beats its parent."""
        node = self._heap[i]
        while i > 0:
            p = self._parent(i)
            if self._heap[p].priority <= node.priority:
                break
            self._swap(i, p)
            i = p

    def _sift_down(self, i: int) -> None:
        """Move node at i toward leaves while a child beats it."""
        n = len(self._heap)
        while True:
            smallest = i
            base = self._d * i + 1
            # Scan up to d children, picking the minimum-priority one.
            for c in range(self._d):
                child = base + c
                if child < n and self._heap[child].priority < self._heap[smallest].priority:
                    smallest = child
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    # ----- public API ------------------------------------------------------

    def insert(self, key: int, value: T) -> None:
        """
        Insert a (key, value) with priority == key by default? No -- here the
        provided `key` is BOTH the identity and the priority, matching the
        base signature `insert(key, value)`. See note in explanation.

        O(log_d n). Raises KeyError on duplicate key.
        """
        if key in self._index:
            raise KeyError(f"Key {key!r} already present; use decrease/increase_key.")
        self._stats.inserts += 1
        node = _Node(key, key, value)  # priority initialized to key
        self._heap.append(node)
        pos = len(self._heap) - 1
        self._index[key] = pos
        self._sift_up(pos)

    def peek(self) -> Optional[Tuple[int, T]]:
        """Return (priority, value) of the minimum without removing. O(1)."""
        if not self._heap:
            return None
        root = self._heap[0]
        return (root.priority, root.value)

    def extract_min(self) -> Optional[Tuple[int, T]]:
        """
        Remove and return (priority, value) of the minimum-priority node.
        O(d * log_d n). Returns None if empty.
        """
        if not self._heap:
            return None
        self._stats.extractions += 1
        root = self._heap[0]
        last = self._heap.pop()
        del self._index[root.key]
        if self._heap:  # there was more than one element
            self._heap[0] = last
            self._index[last.key] = 0
            self._sift_down(0)
        return (root.priority, root.value)

    def decrease_key(self, key: int, new_priority: int) -> bool:
        """
        Lower a key's priority. O(log_d n) via sift-up only.

        Returns:
            True on success, False if key absent or new_priority is not
            actually lower (no-op rejected to preserve heap invariant
            assumptions of callers like Dijkstra).
        """
        self._stats.updates += 1
        pos = self._index.get(key)
        if pos is None:
            return False
        node = self._heap[pos]
        if new_priority > node.priority:
            return False  # not a decrease
        node.priority = new_priority
        self._sift_up(pos)
        return True

    def increase_key(self, key: int, new_priority: int) -> bool:
        """
        Raise a key's priority (higher value = lower priority).
        O(d * log_d n) via sift-down only. Returns False if absent or not
        an actual increase.
        """
        self._stats.updates += 1
        pos = self._index.get(key)
        if pos is None:
            return False
        node = self._heap[pos]
        if new_priority < node.priority:
            return False  # not an increase
        node.priority = new_priority
        self._sift_down(pos)
        return True

    def contains(self, key: int) -> bool:
        """O(1) membership test."""
        self._stats.lookups += 1
        return key in self._index

    def delete(self, key: int) -> bool:
        """
        Delete an arbitrary key. O(d * log_d n).

        Strategy: overwrite the target slot with the last element, fix the
        heap by sifting in whichever direction is needed.

        Returns True if deleted, False if key absent.
        """
        pos = self._index.get(key)
        if pos is None:
            return False
        last_pos = len(self._heap) - 1
        del self._index[key]
        if pos == last_pos:
            self._heap.pop()
            return True
        # Move last element into the hole.
        last = self._heap.pop()
        self._heap[pos] = last
        self._index[last.key] = pos
        # The moved element may need to go up OR down.
        parent = self._parent(pos)
        if pos > 0 and self._heap[pos].priority < self._heap[parent].priority:
            self._sift_up(pos)
        else:
            self._sift_down(pos)
        return True

    def size(self) -> int:
        """O(1)."""
        return len(self._heap)
```

> **Note on `insert(key, value)` signature:** The base class signature only gives `key` and `value`, so I treat `key` as *both* the unique identity and the initial priority (common in graph algorithms where node-id maps to a distance you later decrease). `decrease_key`/`increase_key` then mutate priority while identity stays fixed. If you need decoupled identity vs. priority, change `_Node(key, key, value)` to `_Node(key, priority, value)` and add a `priority` parameter.

---

## Alternative: Pairing Heap

A pairing heap gives **amortized O(1) decrease_key** and is pointer-based, so no index-shifting. I include it because it shines when decrease_key dominates.

```python
class _PNode(Generic[T]):
    __slots__ = ("key", "priority", "value", "child", "sibling", "prev")

    def __init__(self, key: int, priority: int, value: T) -> None:
        self.key = key
        self.priority = priority
        self.value = value
        self.child: Optional[_PNode[T]] = None     # leftmost child
        self.sibling: Optional[_PNode[T]] = None    # next sibling
        self.prev: Optional[_PNode[T]] = None       # parent OR left sibling


class PairingHeapPriorityQueue(PriorityQueue[T]):
    """
    Pairing heap with hash index for O(1) node lookup.

    Time Complexity (amortized):
    - insert:        O(1)
    - peek:          O(1)
    - decrease_key:  O(1) amortized  (cut + meld)
    - extract_min:   O(log n) amortized
    - delete:        O(log n) amortized
    - contains:      O(1)

    Tradeoff: simpler asymptotics for decrease_key than a d-ary heap, but
    pointer-chasing has worse cache behavior, and worst-case (non-amortized)
    bounds are weaker. Great when decrease_key is the hot path.
    """

    def __init__(self) -> None:
        super().__init__()
        self._root: Optional[_PNode[T]] = None
        self._nodes: Dict[int, _PNode[T]] = {}

    def _meld(self, a: Optional[_PNode[T]], b: Optional[_PNode[T]]) -> Optional[_PNode[T]]:
        """Combine two heaps; the smaller root becomes parent. O(1)."""
        if a is None:
            return b
        if b is None:
            return a
        if b.priority < a.priority:
            a, b = b, a
        # b becomes leftmost child of a.
        b.prev = a
        b.sibling = a.child
        if a.child is not None:
            a.child.prev = b
        a.child = b
        a.sibling = None
        a.prev = None
        return a

    def insert(self, key: int, value: T) -> None:
        """O(1). Duplicate keys rejected."""
        if key in self._nodes:
            raise KeyError(f"Key {key!r} already present.")
        self._stats.inserts += 1
        node = _PNode(key, key, value)
        self._nodes[key] = node
        self._root = self._meld(self._root, node)

    def peek(self) -> Optional[Tuple[int, T]]:
        if self._root is None:
            return None
        return (self._root.priority, self._root.value)

    def _detach(self, node: _PNode[T]) -> None:
        """Unlink `node` from its parent/sibling chain. O(1)."""
        if node.prev is None:
            return  # node is root; nothing to detach
        if node.prev.child is node:
            node.prev.child = node.sibling   # prev is parent
        else:
            node.prev.sibling = node.sibling  # prev is left sibling
        if node.sibling is not None:
            node.sibling.prev = node.prev
        node.sibling = None
        node.prev = None

    def decrease_key(self, key: int, new_priority: int) -> bool:
        """O(1) amortized: cut subtree, meld back at root."""
        self._stats.updates += 1
        node = self._nodes.get(key)
        if node is None or new_priority > node.priority:
            return False
        node.priority = new_priority
        if node is not self._root:
            self._detach(node)
            self._root = self._meld(self._root, node)
        return True

    def increase_key(self, key: int, new_priority: int) -> bool:
        """
        Pairing heaps don't support cheap increase-key. We implement it via
        delete + re-insert, preserving value. O(log n) amortized.
        """
        self._stats.updates += 1
        node = self._nodes.get(key)
        if node is None or new_priority < node.priority:
            return False
        value = node.value
        self.delete(key)
        # Re-insert with explicit priority.
        new_node = _PNode(key, new_priority, value)
        self._nodes[key] = new_node
        self._root = self._meld(self._root, new_node)
        return True

    def _merge_pairs(self, first: Optional[_PNode[T]]) -> Optional[_PNode[T]]:
        """Two-pass pairing of the sibling list (the core of extract_min)."""
        if first is None or first.sibling is None:
            return first
        # Pass 1: meld pairs left-to-right.
        pairs: List[_PNode[T]] = []
        a: Optional[_PNode[T]] = first
        while a is not None:
            b = a.sibling
            if b is None:
                a.prev = a.sibling = None
                pairs.append(a)
                break
            nxt = b.sibling
            a.prev = a.sibling = None
            b.prev = b.sibling = None
            pairs.append(self._meld(a, b))
            a = nxt
        # Pass 2: meld right-to-left.
        result = pairs[-1]
        for i in range(len(pairs) - 2, -1, -1):
            result = self._meld(pairs[i], result)
        return result

    def extract_min(self) -> Optional[Tuple[int, T]]:
        """O(log n) amortized."""
        if self._root is None:
            return None
        self._stats.extractions += 1
        root = self._root
        del self._nodes[root.key]
        child = root.child
        if child is not None:
            child.prev = None
        self._root = self._merge_pairs(child)
        return (root.priority, root.value)

    def delete(self, key: int) -> bool:
        """O(log n) amortized."""
        node = self._nodes.get(key)
        if node is None:
            return False
        if node is self._root:
            self.extract_min()
            return True
        self._detach(node)
        del self._nodes[key]
        # Re-meld the deleted node's children back into the heap.
        child = node.child
        if child is not None:
            child.prev = None
            merged = self._merge_pairs(child)
            self._root = self._meld(self._root, merged)
        return True

    def contains(self, key: int) -> bool:
        self._stats.lookups += 1
        return key in self._nodes

    def size(self) -> int:
        return len(self._nodes)
```

---

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| `extract_min`/`peek` on empty heap | Returns `None` |
| Duplicate `insert` | Raises `KeyError` (identity must be unique) |
| `decrease_key` on missing key | Returns `False` |
| `decrease_key` with non-lower priority | Returns `False` (no-op rejected) |
| `increase_key` with non-higher priority | Returns `False` |
| `delete` of root vs. interior vs. last element | All handled distinctly |
| `delete` of last array element | Avoids spurious sift on a popped slot |
| Single-element heap extract | Index map cleared, no sift on empty array |
| `d < 2` | Raises `ValueError` |
| Equal priorities | `<=` in sift-up gives stable-ish behavior, no infinite loops |

---

## Quick Test

```python
def _demo() -> None:
    for PQ in (DaryHeapPriorityQueue, PairingHeapPriorityQueue):
        pq = PQ()
        for k in [50, 30, 70, 10, 90]:
            pq.insert(k, f"v{k}")
        assert pq.peek() == (10, "v10")
        assert pq.decrease_key(90, 5) is True   # 90 -> priority 5
        assert pq.peek() == (5, "v90")
        assert pq.decrease_key(90, 999) is False  # not a decrease
        assert pq.contains(30) and not pq.contains(999)
        assert pq.delete(10) is True
        assert pq.increase_key(30, 100) is True
        out = []
        while pq.size():
            out.append(pq.extract_min()[0])
        assert out == sorted(out), out
        print(f"{PQ.__name__}: OK, stats={pq.stats()}")

if __name__ == "__main__":
    _demo()
```

---

## Tradeoffs: Which to Pick?

| Aspect | D-ary Heap (d=4) | Pairing Heap |
|--------|------------------|--------------|
| `decrease_key` | O(log_d n), real worst case | **O(1) amortized**, worse worst-case |
| `extract_min` | O(d·log_d n) | O(log n) amortized |
| Cache locality | **Excellent** (contiguous array) | Poor (pointer chasing) |
| Memory overhead | Array + index map | 4 pointers/node + map |
| Implementation risk | Low | Higher (pointer surgery) |
| `increase_key` | Native, cheap | Awkward (delete+reinsert) |

**My recommendation:** the **D-ary heap** for the vast majority of cases. Despite the pairing heap's theoretically superior `decrease_key`, the d-ary heap's contiguous-memory layout usually wins in practice (the constant factors and cache effects dominate at realistic `n`). Both satisfy the "not O(n) decrease_key" requirement; the index map is the crucial ingredient that lifts decrease_key from O(n) to O(log n).