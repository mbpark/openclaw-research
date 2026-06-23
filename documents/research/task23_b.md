
### 2.3b: Decrease-Key Operation

**Part B - The Key Challenge:**
```python
    def decrease_key(self, key: int, new_priority: int) -> bool:
        """
        Decrease the priority of an existing key.
        Must be O(log n) or better - O(n) binary heap approach rejected.
        """
        ...

    def increase_key(self, key: int, new_priority: int) -> bool:
        """Increase priority (higher value = lower priority)."""
        ...
```

**What to evaluate for decrease_key:**
- Target O(log n) time complexity
- Requires data structure supporting efficient updates
- Cannot use standard binary heap (would be O(n) to find key)

### 2.3c: Additional Operations

**Part C - Complete Interface:**
```python
    def contains(self, key: int) -> bool:
        """O(1) check for key existence."""
        ...

    def peek(self) -> Optional[Tuple[int, T]]:
        """View minimum without removing."""
        ...

    def delete(self, key: int) -> bool:
        """Delete entry by key."""
        ...

    def stats(self) -> PQOperationStats:
        """Return operation statistics."""
        ...
