"""
Task 3.3: Circuit Breaker Pattern

Implements circuit breaker for external service failure handling.
"""

from typing import Callable, TypeVar, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import time


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0  # seconds
    half_open_max_calls: int = 3
    success_threshold: float = 0.5  # 50% success rate to close


class CircuitBreaker:
    """
    Circuit breaker implementation.
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        self._half_open_successes = 0
    
    @property
    def state(self) -> CircuitState:
        """Check and update state."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            if time.time() - self._last_failure_time > self._config.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                self._half_open_successes = 0
        
        return self._state
    
    def execute(self, operation: Callable) -> any:
        """Execute operation with circuit breaker protection."""
        current_state = self.state
        
        if current_state == CircuitState.CLOSED:
            try:
                result = operation()
                self._record_success()
                return result
            except Exception as e:
                self._record_failure()
                raise
        
        elif current_state == CircuitState.OPEN:
            raise CircuitOpenException("Circuit is open")
        
        else:  # HALF_OPEN
            if self._half_open_calls >= self._config.half_open_max_calls:
                raise CircuitHalfOpenException("Half-open calls exceeded")
            
            self._half_open_calls += 1
            
            try:
                result = operation()
                self._half_open_successes += 1
                self._maybe_close_circuit()
                return result
            except Exception as e:
                self._state = CircuitState.OPEN
                self._last_failure_time = time.time()
                raise
    
    def record_success(self) -> None:
        """Record successful call."""
        self._record_success()
    
    def record_failure(self) -> None:
        """Record failed call."""
        self._record_failure()
    
    def _record_success(self):
        """Record success and maybe close circuit."""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_successes += 1
            self._maybe_close_circuit()
        else:
            self._failure_count = 0
    
    def _record_failure(self):
        """Record failure and maybe open circuit."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.CLOSED and self._failure_count >= self._config.failure_threshold:
            self._state = CircuitState.OPEN
    
    def _maybe_close_circuit(self):
        """Maybe close circuit based on success rate."""
        if self._half_open_successes / self._half_open_calls >= self._config.success_threshold:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
    
    def reset(self) -> None:
        """Reset circuit breaker."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        self._half_open_successes = 0


class CircuitOpenException(Exception):
    """Raised when circuit is open."""
    pass


class CircuitHalfOpenException(Exception):
    """Raised when circuit is half-open and limit exceeded."""
    pass


def test_circuit_breaker():
    """Test circuit breaker functionality."""
    config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=0.1,  # Fast recovery for testing
        half_open_max_calls=2
    )
    
    breaker = CircuitBreaker(config)
    
    # Test initial state
    assert breaker.state == CircuitState.CLOSED
    
    # Test successful operation
    result = breaker.execute(lambda: "success")
    assert result == "success"
    assert breaker.state == CircuitState.CLOSED
    
    # Test failure threshold
    failures = 0
    def failing_operation():
        nonlocal failures
        failures += 1
        raise Exception(f"Failure {failures}")
    
    for _ in range(3):
        try:
            breaker.execute(failing_operation)
        except Exception:
            pass
    
    # Circuit should be open
    assert breaker.state == CircuitState.OPEN
    
    # Test circuit open exception
    try:
        breaker.execute(lambda: "should not execute")
        assert False, "Should have raised CircuitOpenException"
    except CircuitOpenException:
        pass
    
    # Wait for recovery
    time.sleep(0.2)
    assert breaker.state == CircuitState.HALF_OPEN
    
    # Test half-open state
    successes = 0
    def sometimes_succeeds():
        nonlocal successes
        successes += 1
        return "success"
    
    for _ in range(2):
        breaker.execute(sometimes_succeeds)
    
    # Should be closed after success
    assert breaker.state == CircuitState.CLOSED
    
    print("Tests passed")


if __name__ == "__main__":
    test_circuit_breaker()
