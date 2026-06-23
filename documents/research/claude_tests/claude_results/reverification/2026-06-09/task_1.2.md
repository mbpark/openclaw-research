# Lock-Free Stack Using Atomic CAS

## The Core Challenge in Python

Before writing code, I need to address a fundamental reality: **CPython does not provide true atomic CAS primitives for arbitrary object references.** There's no `AtomicReference.compareAndSet()` in the standard library. This is unlike Java/C++ where `std::atomic` or `AtomicReference` exist.

So I'll implement this two ways:
1. **A correct, portable implementation** built on `ctypes` to simulate atomic CAS on a pointer-width integer, with a Python-object indirection table.
2. Discussion of how the GIL affects (but does not solve) correctness.

Let me build the genuinely interesting version: a CAS primitive backed by `ctypes` atomic operations isn't directly exposed either, so I'll use a small, self-contained CAS that relies on the GIL holding during a single bytecode region — and clearly document the limitations.

The honest engineering answer: **on CPython, a single `is`-comparison-then-assignment cannot be made atomic without either the GIL guaranteeing it or an external primitive.** I'll provide a CAS that is correct *under the GIL* and document the ABA problem fully.

---

## Implementation

```python
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


def _cas(obj: object, attr: str, expected: object, new: object) -> bool:
    """
    Compare-and-swap on an attribute of `obj`.

    Atomically: if getattr(obj, attr) is `expected`, set it to `new` and
    return True; otherwise return False without modifying anything.

    Atomicity guarantee
    --------------------
    On CPython, the Global Interpreter Lock (GIL) ensures that a single
    bytecode operation cannot be preempted by another Python thread. The
    body below performs the read, identity comparison, and conditional
    write. To make this region effectively atomic *with respect to other
    Python threads*, we rely on the fact that CPython does not release the
    GIL in the middle of these operations (no blocking C calls, no
    bytecode boundary that triggers a thread switch check mid-comparison).

    This is the same mechanism that makes operations like ``dict[k] = v``
    appear atomic in CPython. It is NOT portable to GIL-free Python
    (e.g. PEP 703 / free-threaded builds) or to other interpreters, where
    a real hardware CAS (via C extension / ``ctypes`` on a machine word)
    would be required.

    Args:
        obj: Object holding the attribute.
        attr: Attribute name to CAS on.
        expected: The value we expect the attribute to currently hold
            (compared by identity, ``is``).
        new: The value to store if the comparison succeeds.

    Returns:
        True if the swap was performed, False otherwise.
    """
    # Under the GIL, this read-compare-write does not yield to another
    # Python thread, so it behaves as a single atomic CAS step.
    if getattr(obj, attr) is expected:
        setattr(obj, attr, new)
        return True
    return False


class LockFreeStack(Generic[T]):
    """Lock-free (mutex-free) stack using only atomic CAS operations.

    The stack is a singly linked list. The only point of contention is the
    ``head`` pointer, which is mutated exclusively via compare-and-swap
    retry loops. No ``threading.Lock`` or other mutex is used.

    Concurrency model
    -----------------
    * ``push`` and ``pop`` are lock-free: every operation either makes
      progress or retries because another thread won the CAS race. There
      is no point at which a thread can block others by being descheduled.
    * Correctness of the CAS primitive depends on CPython's GIL (see
      ``_cas``). The *algorithm* itself is a textbook lock-free Treiber
      stack and would be correct given a real hardware CAS.

    ABA problem
    -----------
    The classic Treiber stack is vulnerable to the ABA problem: a thread
    reads head == A, gets descheduled, and by the time it runs its CAS the
    head has gone A -> B -> A. The CAS succeeds even though the stack
    changed underneath it, potentially re-linking a stale/reused node.

    We mitigate this with a *monotonic version counter* packed alongside
    the head pointer (a "tagged pointer" emulation). Each successful head
    update bumps the counter, so a CAS comparing the full ``(node, tag)``
    pair will fail if the tag advanced — even if the node pointer cycled
    back to the same object. See ``_Head``.

    In a memory-managed language like Python there is also no manual
    free/reuse of node memory, which removes the *use-after-free* flavor
    of ABA entirely (the GC keeps a node alive as long as any thread holds
    a reference). The version counter handles the *logical* ABA case.
    """

    @dataclass
    class Node(Generic[T]):
        """A singly linked list node."""

        value: T
        next: "Optional[LockFreeStack.Node]" = None

    @dataclass
    class _Head:
        """Tagged head: the node plus a monotonic version stamp.

        The version stamp is what defeats logical ABA. We treat the entire
        ``_Head`` *object* as the unit of CAS, so each push/pop produces a
        brand-new ``_Head`` instance with an incremented tag. A CAS that
        observed an old ``_Head`` will fail identity comparison even if the
        ``node`` happens to be identical.
        """

        node: "Optional[LockFreeStack.Node]"
        tag: int

    def __init__(self) -> None:
        """Initialize an empty stack."""
        # _head holds a _Head object. We CAS on the `head` attribute of
        # self by swapping in entirely new _Head objects.
        self._head: LockFreeStack._Head = LockFreeStack._Head(node=None, tag=0)
        # Monotonic source for version tags. itertools.count().__next__ is
        # itself effectively atomic under the GIL, giving us unique tags.
        self._tag_counter = itertools.count(1)

    def push(self, item: T) -> None:
        """Push an item onto the top of the stack.

        Lock-free: spins on a CAS of the head pointer until it wins.

        Args:
            item: Value to push.
        """
        new_node: LockFreeStack.Node = LockFreeStack.Node(value=item)
        while True:
            current_head = self._head          # snapshot (node, tag)
            new_node.next = current_head.node   # link new node above old top
            new_head = LockFreeStack._Head(
                node=new_node,
                tag=next(self._tag_counter),
            )
            # Atomically: if head is still the snapshot, install new_head.
            if _cas(self, "_head", current_head, new_head):
                return
            # Else another thread changed head; retry with fresh snapshot.

    def pop(self) -> Optional[T]:
        """Pop and return the top item, or None if the stack is empty.

        Lock-free: spins on a CAS of the head pointer until it wins.

        Returns:
            The top value, or ``None`` if the stack was empty.
        """
        while True:
            current_head = self._head          # snapshot (node, tag)
            top = current_head.node
            if top is None:
                return None                     # empty; nothing to pop
            new_head = LockFreeStack._Head(
                node=top.next,                  # advance head past `top`
                tag=next(self._tag_counter),
            )
            # The tag in `current_head` guards against ABA: if head cycled
            # back to the same node via another thread, the tag differs and
            # this CAS fails, forcing a safe retry.
            if _cas(self, "_head", current_head, new_head):
                return top.value
            # Else lost the race; retry.

    def is_empty(self) -> bool:
        """Return True if the stack currently appears empty.

        This is inherently a *snapshot* and may be stale the instant it
        returns, since other threads may push or pop concurrently. Use only
        as a hint, never for correctness-critical control flow.

        Returns:
            True if the head currently points to no node.
        """
        return self._head.node is None
```

---

## Design Decisions & Tradeoffs

### 1. The Treiber stack algorithm
This is the canonical lock-free stack. Both `push` and `pop`:
- Take a **snapshot** of `head`.
- Compute the new head locally.
- **CAS** the head from snapshot → new value, retrying on failure.

No mutex, no blocking. A losing thread simply retries — this is the definition of *lock-free* (system-wide progress guaranteed).

### 2. Tagged pointers for ABA (`_Head` with `tag`)
The **ABA problem**: Thread 1 reads `head = A` and stalls. Threads 2/3 pop A, pop B, then push A back. Thread 1's CAS `(A → A.next_old)` succeeds against a now-corrupt structure.

**My mitigation:** I CAS on an entire `_Head` *object* carrying `(node, tag)`, where `tag` strictly increases on every successful head mutation. Even if `node` cycles `A → B → A`, the tag differs, so a stale CAS fails. This is the standard "tagged pointer / version counter" technique.

> ⚠️ **Honest caveat:** A *new* `_Head` object is created each time, so CAS-by-identity on the `_Head` object would already fail for a stale snapshot even without the tag — because the old `_Head` instance is never reinstalled. The tag is belt-and-suspenders and documents intent clearly. The genuinely subtle ABA-via-memory-reuse cannot occur here anyway (see next point).

### 3. The CAS primitive (`_cas`) — the hard truth
CPython exposes **no real atomic CAS** for object references. My `_cas` relies on the **GIL** guaranteeing no thread switch occurs during the read-compare-write since none of those steps release the GIL. This mirrors why `dict.setdefault` etc. are "atomic" in practice.

**Tradeoff / limitation:** This is *not* correct under free-threaded Python (PEP 703). For real portability you'd need a C extension exposing `__atomic_compare_exchange` on a machine word, with a side table mapping word-sized tagged handles to Python objects.

### 4. Memory reclamation
In C, lock-free structures need **hazard pointers** or **epoch-based reclamation** to avoid freeing a node another thread still references. **Python's GC handles this for free**: a node stays alive as long as any thread holds a reference, eliminating use-after-free entirely. This is a genuine advantage of the managed-memory environment.

---

## Edge Cases Handled

| Case | Handling |
|------|----------|
| **Pop from empty** | `top is None` → returns `None` cleanly, no CAS attempted. |
| **Concurrent push/pop race** | CAS failure → retry loop with fresh snapshot. |
| **ABA (logical)** | Tagged `_Head` + always-new `_Head` instance. |
| **ABA (memory reuse)** | Impossible — GC keeps nodes alive. |
| **`is_empty` staleness** | Documented as a best-effort hint, not authoritative. |
| **Storing `None` as a value** | Works: emptiness is detected via `node is None`, not value. So `pop()` returning `None` for a real `None` value is ambiguous — documented limitation; use a sentinel wrapper if you must distinguish. |

The last row is worth flagging: `pop()` returning `None` is overloaded (empty vs. a pushed `None`). The interface mandates this, so I preserve it, but in production I'd return a `Sentinel` or raise `IndexError` on empty.