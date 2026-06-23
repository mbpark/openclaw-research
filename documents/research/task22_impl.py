"""
Task 2.2: Database Connection Pool

Thread-safe connection pool with:
- Concurrent connection management
- Connection lifecycle tracking
- Resource constraints
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from threading import Lock
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConnectionState:
    in_use: bool = False
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    usage_count: int = 0

class DatabaseConnectionPool:
    """
    Manages a pool of database connections.
    
    Provides thread-safe connection acquisition and release
    with automatic cleanup and resource monitoring.
    """
    
    def __init__(
        self, 
        min_connections: int = 1,
        max_connections: int = 10,
        idle_timeout: float = 300.0,
        max_lifetime: Optional[float] = None
    ):
        self._pool: List[Any] = []
        self._connection_states: Dict[int, ConnectionState] = {}
        self._min_connections = min_connections
        self._max_connections = max_connections
        self._idle_timeout = idle_timeout
        self._max_lifetime = max_lifetime
        self._lock = Lock()
        self._initialized = False
        
        # Statistics
        self._total_created = 0
        self._total_destroyed = 0
        self._total_acquired = 0
        self._total_failed_acquires = 0
    
    def initialize(self) -> bool:
        """Initialize the connection pool."""
        with self._lock:
            if self._initialized:
                return False
            
            try:
                for _ in range(self._min_connections):
                    connection = self._create_connection()
                    self._add_connection(connection)
                
                self._initialized = True
                logger.info(f"Connection pool initialized with {self._min_connections} connections")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                return False
    
    def acquire_connection(self, timeout: Optional[float] = None) -> Optional[Any]:
        """Acquire a connection from the pool."""
        with self._lock:
            self._cleanup_expired_connections()
            
            # Try to get an existing idle connection
            for connection in self._pool:
                if connection and not self._connection_states[connection["connection_id"]].in_use:
                    self._mark_connection_used(connection)
                    return connection
            
            # Create new connection if under max limit
            if len(self._pool) < self._max_connections:
                try:
                    connection = self._create_connection()
                    self._mark_connection_used(connection)
                    return connection
                except Exception as e:
                    logger.warning(f"Failed to create new connection: {e}")
        
        self._total_failed_acquires += 1
        return None
    
    def release_connection(self, connection: Any) -> None:
        """Release a connection back to the pool."""
        if connection is None:
            return
        
        with self._lock:
            connection_id = connection["connection_id"]
            if connection_id in self._connection_states:
                self._connection_states[connection_id].in_use = False
                self._connection_states[connection_id].last_used_at = time.time()
                self._connection_states[connection_id].usage_count += 1
    
    def close_all(self) -> None:
        """Close and remove all connections."""
        with self._lock:
            for connection in self._pool:
                self._destroy_connection(connection)
            self._pool.clear()
            self._connection_states.clear()
            self._initialized = False
    
    def get_pool_stats(self) -> Dict[str, int]:
        """Get current pool statistics."""
        with self._lock:
            active_connections = sum(1 for state in self._connection_states.values() 
                                   if state.in_use)
            
            return {
                "total_connections": len(self._pool),
                "active_connections": active_connections,
                "idle_connections": len(self._pool) - active_connections,
                "min_connections": self._min_connections,
                "max_connections": self._max_connections,
                "total_created": self._total_created,
                "total_destroyed": self._total_destroyed,
                "total_acquired": self._total_acquired,
                "total_failed_acquires": self._total_failed_acquires
            }
    
    def _create_connection(self) -> Any:
        """Create a new connection (abstract implementation)."""
        connection_id = self._total_created + 1
        self._total_created += 1
        return {"connection_id": connection_id, "status": "open"}
    
    def _destroy_connection(self, connection: Any) -> None:
        """Destroy a connection."""
        try:
            connection_id = connection["connection_id"]
            if isinstance(connection, dict):
                connection["status"] = "closed"
            
            self._total_destroyed += 1
            self._connection_states.pop(connection_id, None)
        except Exception as e:
            logger.warning(f"Failed to close connection: {e}")
    
    def _add_connection(self, connection: Any) -> None:
        """Add a connection to the pool."""
        self._pool.append(connection)
        connection_id = connection["connection_id"]
        self._connection_states[connection_id] = ConnectionState()
    
    def _mark_connection_used(self, connection: Any) -> None:
        """Mark a connection as in use."""
        connection_id = connection["connection_id"]
        self._connection_states[connection_id].in_use = True
        self._connection_states[connection_id].last_used_at = time.time()
        self._total_acquired += 1
    
    def _cleanup_expired_connections(self) -> None:
        """Remove expired connections."""
        current_time = time.time()
        connections_to_remove = []
        
        for connection_id, state in self._connection_states.items():
            if not state.in_use:
                if current_time - state.last_used_at > self._idle_timeout:
                    connections_to_remove.append(connection_id)
                    continue
                
                if self._max_lifetime and current_time - state.created_at > self._max_lifetime:
                    connections_to_remove.append(connection_id)
        
        for connection_id in connections_to_remove:
            connection = None
            for conn in self._pool:
                if conn["connection_id"] == connection_id:
                    connection = conn
                    break
            if connection:
                self._destroy_connection(connection)
                self._pool.remove(connection)
        
        for connection_id in connections_to_remove:
            self._connection_states.pop(connection_id, None)

# Example implementation for testing
class MockConnectionPool(DatabaseConnectionPool):
    def _create_connection(self) -> Any:
        connection_id = self._total_created + 1
        self._total_created += 1
        return {"connection_id": connection_id, "connected": True}
    
    def _destroy_connection(self, connection: Any) -> None:
        connection["connected"] = False

def run_tests() -> bool:
    """Run comprehensive tests for the connection pool."""
    pool = MockConnectionPool(min_connections=2, max_connections=5)
    
    # Test 1: Initialization
    if not pool.initialize():
        print("FAILED: Pool initialization")
        return False
    
    # Test 2: Initial connection count
    stats = pool.get_pool_stats()
    if stats["total_connections"] != 2:
        print(f"FAILED: Initial connection count. Expected 2, got {stats['total_connections']}")
        return False
    
    # Test 3: Connection acquisition
    conn1 = pool.acquire_connection()
    if not conn1:
        print("FAILED: Could not acquire connection")
        return False
    
    stats = pool.get_pool_stats()
    if stats["active_connections"] != 1:
        print("FAILED: Active connection count incorrect")
        return False
    
    # Test 4: Connection release
    pool.release_connection(conn1)
    stats = pool.get_pool_stats()
    if stats["active_connections"] != 0:
        print("FAILED: Connection not properly released")
        return False
    
    # Test 5: Multiple connections
    conn2 = pool.acquire_connection()
    conn3 = pool.acquire_connection()
    if conn2 is None or conn3 is None:
        print("FAILED: Could not acquire multiple connections")
        return False
    
    # Test 6: Max connections limit
    stats = pool.get_pool_stats()
    if stats["total_connections"] > 5:
        print("FAILED: Exceeded max connections")
        return False
    
    # Test 7: Cleanup
    pool.release_connection(conn1)
    pool.release_connection(conn2)
    pool.release_connection(conn3)
    pool.close_all()
    
    stats = pool.get_pool_stats()
    if stats["total_connections"] != 0:
        print("FAILED: Connections not properly cleaned up")
        return False
    
    print("All connection pool tests passed!")
    return True

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    run_tests()
