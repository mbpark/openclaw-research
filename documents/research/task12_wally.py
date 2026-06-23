"""
Task 1.2: Lock-Free Stack Using Atomic CAS

This implementation uses only compare-and-swap operations for true lock-free
synchronization. No threading primitives are used.

Key considerations:
1. Uses ctypes for CAS operations on object references
2. Handles the ABA problem through reference counting (but doesn't fully solve it)
3. Memory management is a known issue - this implementation has potential for
   premature garbage collection of popped nodes
"""

from typing import Optional, TypeVar
from dataclasses import dataclass
import ctypes


T = TypeVar('T')


class AtomicRef:
    """
    Atomic reference supporting compare-and-swap operations.
    
    Uses ctypes' compare_and_swap for lock-free manipulation of references.
    """
    
    def __init__(self, value):
        self._value = ctypes.c_long(ctypes.cast(value, ctypes.c_void_p).value)
    
    def load(self) -> int:
        """Return current value as integer reference."""
        return self._value.value
    
    def compare_and_swap(self, expected: int, new_value: int) -> bool:
        """
        Atomically swap value if it equals expected.
        
        Returns True if the swap succeeded, False otherwise.
        """
        return ctypes.compare_and_swap(
            self._value, 
            ctypes.c_long(new_value), 
            ctypes.c_long(expected)
        )
    
    def compare_and_swap_ref(self, expected: Optional[object], new: Optional[object]) -> bool:
        """CAS on object references for convenience."""
        expected_int = ctypes.cast(expected, ctypes.c_void_p).value if expected else 0
        new_int = ctypes.cast(new, ctypes.c_void_p).value if new else 0
        return self.compare_and_swap(expected_int, new_int)


class LockFreeStack:
    """
    Lock-free stack using only atomic CAS operations.
    
    This implementation uses a head pointer protected by CAS operations.
    Each operation uses a spin-wait loop until it succeeds.
    
    Important notes:
    1. This implementation does not fully solve the ABA problem
    2. Memory management is not handled - popped nodes may be garbage collected
       while other threads still reference them
    3. A production implementation should use hazard pointers or a similar scheme
    """
    
    @dataclass
    class Node:
        value: T
        next_node: 'Optional[Node]' = None
    
    def __init__(self):
        """Initialize empty stack."""
        self._head: AtomicRef = AtomicRef(None)
    
    def push(self, item: T) -> None:
        """
        Push item onto stack. Lock-free.
        
        Uses a CAS loop - if head changes during the operation, retry.
        This ensures no concurrent push corrupts the stack.
        """
        new_node = self.Node(item, None)
        
        # Spin until CAS succeeds
        while True:
            # Load current head
            head = self._head.load()
            
            # Set new node's next to current head
            # This is where the ABA problem could occur
            # If another thread changes head and then changes it back to same
            # value, our node could point to a different node with same address
            new_node.next_node = ctypes.cast(head, ctypes.py_object).value if head else None
            
            # Attempt to update head
            new_head_int = ctypes.cast(new_node, ctypes.c_void_p).value
            if self._head.compare_and_swap(head, new_head_int):
                break
    
    def pop(self) -> Optional[T]:
        """
        Pop and return top item. Returns None if empty.
        Lock-free.
        
        Uses a CAS loop to ensure consistency.
        """
        # Spin until we successfully pop or stack is empty
        while True:
            # Load current head
            head = self._head.load()
            
            if head == 0:  # Empty stack
                return None
            
            # Get head node
            head_node = ctypes.cast(head, ctypes.py_object).value
            
            # Set new head to head's next
            next_node = head_node.next_node
            next_int = ctypes.cast(next_node, ctypes.c_void_p).value if next_node else 0
            
            # Attempt to update head
            if self._head.compare_and_swap(head, next_int):
                return head_node.value
            
            # CAS failed, retry with new head
    
    def is_empty(self) -> bool:
        """
        Returns True if stack is empty. Note: this is inherently
        eventually-consistent, so use with caution.
        """
        return self._head.load() == 0


def test_lock_free_stack():
    """Basic tests for the lock-free stack."""
    
    stack = LockFreeStack()
    
    # Test basic operations
    assert stack.is_empty()
    assert stack.pop() is None
    
    stack.push(1)
    stack.push(2)
    stack.push(3)
    
    assert not stack.is_empty()
    assert stack.pop() == 3
    assert stack.pop() == 2
    assert stack.pop() == 1
    assert stack.pop() is None
    assert stack.is_empty()
    
    print("Basic functionality tests passed")
    
    # Test concurrent operations
    stack2 = LockFreeStack()
    push_count = [0]
    pop_count = [0]
    errors = []
    
    def push_worker(n: int):
        try:
            for i in range(n):
                stack2.push(i)
                push_count[0] += 1
        except Exception as e:
            errors.append(e)
    
    def pop_worker():
        try:
            count = 0
            while count < 1000 and (push_count[0] > 0 or not stack2.is_empty()):
                stack2.pop()
                pop_count[0] += 1
                count += 1
        except Exception as e:
            errors.append(e)
    
    import threading
    
    push_threads = [threading.Thread(target=push_worker, args=(500,)) for _ in range(5)]
    pop_threads = [threading.Thread(target=pop_worker) for _ in range(5)]
    
    for t in push_threads:
        t.start()
    
    for t in pop_threads:
        t.start()
    
    for t in push_threads:
        t.join()
    
    for t in pop_threads:
        t.join()
    
    print(f"Concurrent test: pushed {push_count[0]}, popped {pop_count[0]}, errors: {len(errors)}")


if __name__ == "__main__":
    test_lock_free_stack()
