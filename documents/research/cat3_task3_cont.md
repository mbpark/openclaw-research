
    def record_success(self) -> None:
        """Record successful call."""
        ...

    def record_failure(self) -> None:
        """Record failed call."""
        ...

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        ...


class CircuitOpenException(Exception):
    """Raised when circuit is open."""
    pass


class CircuitHalfOpenException(Exception):
    """Raised when circuit is half-open and limit exceeded."""
    pass
```

**What to evaluate:**
- Correct state transitions
- Failure counting and threshold detection
- Timer for recovery attempts
- Half-open state management

**Scoring:** __ / 6

---
# Checkpoint 2

**Decision:** ☐ Continue ☐ Adjust ☐ Stop
