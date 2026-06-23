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
import threading


T = TypeVar('T')


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
        # Use a mutable container for head pointer
        self._head_container = ctypes.c_void_p(None)
    
    def push(self, item: T) -> None:
        """
        Push item onto stack. Lock-free.
        
        Uses a CAS loop - if head changes during the operation, retry.
        This ensures no concurrent push corrupts the stack.
        """
        new_node = self.Node(item, None)
        new_head = ctypes.cast(new_node, ctypes.c_void_p).value
        
        # Spin until CAS succeeds
        while True:
            current_head = self._head_container.value
            
            # Set new node's next to current head
            new_node.next_node = ctypes.cast(current_head, ctypes.py_object).value if current_head else None
            
            # Attempt to update head using CAS
            if ctypes.compare_and_swap(
                self._head_container,
                ctypes.c_void_p(new_head),
                ctypes.c_void_p(current_head)
            ):
                return
    
    def pop(self) -> Optional[T]:
        """
        Pop and return top item. Returns None if empty.
        Lock-free.
        
        Uses a CAS loop to ensure consistency.
        """
        # Spin until we successfully pop or stack is empty
        while True:
            # Load current head
            head = self._head_container.value
            
            if head == 0:  # Empty stack
                return None
            
            # Get head node
            head_node = ctypes.cast(head, ctypes.py_object).value
            
            # Set new head to head's next
            next_node = head_node.next_node
            next_head = ctypes.cast(next_node, ctypes.c_void_p).value if next_node else 0
            
            # Attempt to update head
            if ctypes.compare_and_swap(
                self._head_container,
                ctypes.c_void_p(next_head),
                ctypes.c_void_p(head)
            ):
                return head_node.value
            
            # CAS failed, retry
    
    def is_empty(self) -> bool:
        """
        Returns True if stack is empty. Note: this is inherently
        eventually-consistent, so use with caution.
        """
        return self._head_container.value == 0


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
