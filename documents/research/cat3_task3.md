
    def get_state(self) -> AccountState:
        """Rebuild current state from events."""
        ...

    def get_history(self) -> List[Event]:
        """Return event history."""
        ...


class CachedAccountProjection:
    """
    Maintains up-to-date state without full replay.
    """
    def __init__(self, repository: AccountRepository):
        self._repository = repository
        self._cache: dict = {}

    def handle_event(self, event: Event):
        """Update projection when new event arrives."""
        ...

    def get_state(self, aggregate_id: str) -> Optional[AccountState]:
        """Get current state from projection."""
        ...
```

**What to evaluate:**
- Events are immutable with sequential IDs
- Aggregates rebuild from event stream
- Aggregate rejects events causing invalid state
- Projection implementation for efficient querying

**Scoring:** __ / 6

---

## Task 3.3: Circuit Breaker Pattern

**Description:**
Implement circuit breaker for external service failure handling.

**Interface:**
```python
from typing import Callable, TypeVar
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import time


class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Fail fast
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0  # seconds
    half_open_max_calls: int = 3
    success_threshold: float = 0.5  # 50% success rate to close


class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig = None):
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        self._half_open_successes = 0

    @property
    def state(self) -> CircuitState:
        """Check and update state."""
        ...

    def execute(self, operation: Callable) -> any:
        """Execute operation with circuit breaker protection."""
        ...
