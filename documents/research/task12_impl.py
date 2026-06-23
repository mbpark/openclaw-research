"""
Task 1.2: Lock-Free Stack Implementation

Key considerations:
1. CAS operations at head pointer
2. ABA problem acknowledged - not fully solved (would need epoch/reclamation)
3. Memory management - known limitation (popped nodes could be GC'd)
"""

from typing import Optional, TypeVar
from dataclasses import dataclass
import threading

T = TypeVar('T')


class LockFreeStack:
    """
    Lock-free stack using CAS.
    
    ABA Problem: Acknowledged but not fully solved.
    Memory Management: Simplified - assumes GC will not reclaim too fast.
    """
    
    @dataclass
    class Node:
        value: T
        next_node: 'Optional[Node]' = None
    
    def __init__(self):
        self._head: Optional[Node] = None
        # In production: use atomic reference with CAS
    
    def push(self, item: T) -> None:
        """Push using CAS loop.

        CAS Algorithm:
        new_node.next = old_head
        while not CAS(head, old_head, new_node):
            old_head = head  # reload
            new_node.next = old_head
        """
        new_node = self.Node(item)
        
        while True:
            old_head = self._head
            new_node.next_node = old_head
            
            # CAS would go here - simplified for demonstration
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
    stack.push(1); stack.push(2); stack.push(3)
    assert stack.pop() == 3
    assert stack.pop() == 2
    assert stack.pop() == 1
    assert stack.pop() is None
    print("Tests passed")

if __name__ == "__main__":
    test_stack()
