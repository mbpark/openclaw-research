"""
Task 1.3: Database Connection Pool

Implementation with:
- Thread safety via single RLock
- Idle connection expiration
- Blocking acquire with timeout
- Connection failure handling
"""

from typing import Protocol, Callable, Optional
from dataclasses import dataclass
import threading
import time


class Connection(Protocol):
    def execute(self, query: str) -> list: ...
    def close(self) -> None: ...


class ConnectionPool:
    """Thread-safe database connection pool."""
    
    @dataclass
    class State:
        active: int = 0
        idle: int = 0
        total: int = 0
        max_size: int = 10
        created: int = 0
        destroyed: int = 0
    
    def __init__(
        self,
        create_fn: Callable[[], Connection],
        max_size: int = 10,
        idle_timeout: float = 300.0
    ):
        self._create_fn = create_fn
        self._max_size = max_size
        self._idle_timeout = idle_timeout
        self._idle: list = []
        self._active: set = set()
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._closed = False
        self._stats = self.State(max_size=max_size)
    
    def _evict_idle(self):
        """Remove expired idle connections."""
        now = time.time()
        new_idle = []
        for conn, timestamp in self._idle:
            if now - timestamp < self._idle_timeout:
                new_idle.append((conn, timestamp))
            else:
                try:
                    conn.close()
                    self._stats.destroyed += 1
                    self._stats.total -= 1
                except:
                    pass
        self._idle = new_idle
    
    def acquire(self, timeout: Optional[float] = None) -> Connection:
        """Acquire a connection, waiting up to timeout."""
        deadline = None if timeout is None else time.time() + timeout
        
        with self._condition:
            if self._closed:
                raise RuntimeError("Pool is closed")
            
            while True:
                self._evict_idle()
                
                # Try to get idle connection
                while self._idle:
                    try:
                        conn, _ = self._idle.pop(0)
                        self._active.add(conn)
                        self._stats.active = len(self._active)
                        self._stats.idle = len(self._idle)
                        return conn
                    except Exception:
                        continue
                
                # Create new connection if under limit
                if self._stats.total < self._max_size:
                    conn = self._create_fn()
                    self._active.add(conn)
                    self._stats.active = len(self._active)
                    self._stats.total += 1
                    self._stats.created += 1
                    return conn
                
                # Wait for connection or timeout
                if timeout is not None:
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        raise TimeoutError("Acquire timed out")
                    if not self._condition.wait(timeout=remaining):
                        raise TimeoutError("Acquire timed out")
                else:
                    self._condition.wait()
    
    def release(self, conn: Connection, is_healthy: bool = True) -> None:
        """Release connection back to pool."""
        with self._condition:
            self._active.discard(conn)
            
            if is_healthy and not self._closed:
                self._idle.append((conn, time.time()))
                self._stats.idle = len(self._idle)
            else:
                try:
                    conn.close()
                    self._stats.total -= 1
                    self._stats.destroyed += 1
                except:
                    pass
            
            self._stats.active = len(self._active)
            self._condition.notify()
    
    def close(self, timeout: Optional[float] = None) -> None:
        """Close pool, draining active connections."""
        with self._condition:
            self._closed = True
            self._condition.notify_all()
            
            # Close all idle connections
            for conn, _ in self._idle:
                try:
                    conn.close()
                except:
                    pass
            self._idle.clear()
            
            self._stats.total -= self._stats.idle
            self._stats.idle = 0
    
    @property
    def state(self) -> State:
        return self.State(
            active=len(self._active),
            idle=len(self._idle),
            total=self._stats.total,
            max_size=self._max_size,
            created=self._stats.created,
            destroyed=self._stats.destroyed
        )
    
    @property
    def is_closed(self) -> bool:
        return self._closed


def test_pool():
    """Basic tests."""
    class FakeConnection:
        def execute(self, query): return []
        def close(self): pass
    
    pool = ConnectionPool(lambda: FakeConnection(), max_size=3)
    
    c1 = pool.acquire()
    assert isinstance(c1, FakeConnection)
    
    pool.release(c1)
    assert pool.state.idle == 1
    
    c2 = pool.acquire()
    assert pool.state.active == 1
    
    pool.close()
    print("Tests passed")

if __name__ == "__main__":
    test_pool()
