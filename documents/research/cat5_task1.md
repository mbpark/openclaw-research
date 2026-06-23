## Task 5.2: Idempotency Keys for Payment Processing

**Description:**
Implement idempotency key system to prevent duplicate payments.

**Interface:**
```python
from typing import Callable, Optional, TypeVar
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid
import time


class IdempotencyState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class IdempotencyEntry:
    idempotency_key: str
    operation: str
    state: IdempotencyState
    result: Optional[any]
    created_at: datetime
    expires_at: datetime


class IdempotencyStore:
    """
    Store for tracking idempotency states.
    """
    
    def create_entry(
        self,
        key: str,
        operation: str,
        timeout: float = 300.0
    ) -> Optional[IdempotencyEntry]:
        """
        Create new idempotency entry.
        Returns entry if created, None if key already exists.
        """
        ...

    def update_entry(
        self,
        key: str,
        result: any
    ) -> bool:
        """Mark entry as completed."""
        ...

    def get_entry(self, key: str) -> Optional[IdempotencyEntry]:
        """Retrieve entry by key."""
        ...

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        ...


class IdempotencyGuard:
    """
    Decorator/context manager for idempotent operations.
    """
    
    def __init__(
        self,
        store: IdempotencyStore,
        operation: str,
        timeout: float = 300.0
    ):
        self._store = store
        self._operation = operation
        self._timeout = timeout

    def execute(
        self,
        idempotency_key: str,
        func: Callable
    ) -> any:
        """
        Execute function with idempotency protection.
        If key already exists and completed, return cached result.
        """
        entry = self._store.get_entry(idempotency_key)
        
        if entry and entry.state == IdempotencyState.COMPLETED:
            return entry.result
        
        # Create new entry
        new_entry = self._store.create_entry(
            idempotency_key,
            self._operation,
            self._timeout
        )
        
        if new_entry:
            try:
                result = func()
                self._store.update_entry(idempotency_key, result)
                return result
            except Exception as e:
                # Handle failure case
                raise
        else:
            raise Exception("Duplicate request - same idempotency key already exists")
```

**What to evaluate:**
- Proper state tracking (not just completed)
- Timeout handling for long operations
- Distinguishes "not started" vs "in progress" vs "completed"
- Race condition prevention

**Scoring:** __ / 6
