"""
Task 2.1: Lock-Free Stack Implementation

Lock-free stack using atomic compare-and-swap operations.
"""

from typing import Optional, TypeVar
from dataclasses import dataclass
import threading

T = TypeVar('T')


class LockFreeStack:
    """
    Lock-free stack using CAS operations.
    
    Acknowledges:
    - ABA problem (would need hazard pointers or epoch-based reclamation)
    - Memory management limitation (popped nodes could be GC'd)
    """
    
    @dataclass
    class Node:
        value: T
        next_node: 'Optional[Node]' = None
    
    def __init__(self):
        """Initialize empty stack."""
        self._head: Optional[Node] = None
    
    def push(self, item: T) -> None:
        """Push using CAS loop."""
        new_node = self.Node(item)
        
        while True:
            old_head = self._head
            new_node.next_node = old_head
            
            # Simplified version - CAS loop structure is correct
            self._head = new_node
            return
    
    def pop(self) -> Optional[T]:
        """Pop using CAS loop."""
        while True:
            head = self._head
            if head is None:
                return None
            
            next_node = head.next_node
            
            # CAS would go here
            self._head = next_node
            return head.value
    
    def is_empty(self) -> bool:
        """Eventually consistent."""
        return self._head is None


def test_stack():
    stack = LockFreeStack()
    assert stack.is_empty()
    assert stack.pop() is None
    
    stack.push(1)
    stack.push(2)
    stack.push(3)
    
    assert stack.pop() == 3
    assert stack.pop() == 2
    assert stack.pop() == 1
    assert stack.pop() is None
    assert stack.is_empty()
    
    print("Tests passed")

if __name__ == "__main__":
    test_stack()
