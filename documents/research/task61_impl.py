"""
Task 6.1: "Build a Cache"

Initial underspecified request. Ask questions, define scope, then build.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from threading import Lock
import time


class EvictionPolicy(Enum):
    LRU = "lru"
    LFU = "lfu"
    LIFO = "fifo"


@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: float
    last_accessed: float
    frequency: int = 0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        if not self.ttl:
            return False
        return time.time() - self.created_at > self.ttl


class CacheConfig:
    """Configuration for cache."""
    def __init__(
        self,
        max_size: int = 1000,
        eviction_policy: EvictionPolicy = EvictionPolicy.LRU,
        default_ttl: Optional[float] = None
    ):
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self.default_ttl = default_ttl


class CacheStats:
    """Cache statistics."""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class Cache:
    """
    In-memory cache with configurable eviction.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self._config = config or CacheConfig()
        self._entries: Dict[str, CacheEntry] = {}
        self._access_order: list = []
        self._stats = CacheStats()
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            entry = self._entries.get(key)
            if entry is None or entry.is_expired():
                self._stats.misses += 1
                if entry and entry.is_expired():
                    del self._entries[key]
                    if key in self._access_order:
                        self._access_order.remove(key)
                    self._stats.expirations += 1
                return None
            
            entry.last_accessed = time.time()
            entry.frequency += 1
            self._update_access_order(key)
            self._stats.hits += 1
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value in cache."""
        with self._lock:
            # Remove existing key if present
            if key in self._entries:
                del self._entries[key]
                if key in self._access_order:
                    self._access_order.remove(key)
            
            # Evict if at capacity
            while len(self._entries) >= self._config.max_size:
                self._evict()
            
            self._entries[key] = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl or self._config.default_ttl
            )
            self._access_order.append(key)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._entries:
                del self._entries[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False
    
    def size(self) -> int:
        return len(self._entries)
    
    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._access_order.clear()
    
    def get_stats(self) -> CacheStats:
        return self._stats
    
    def _evict(self) -> None:
        """Evict an entry based on policy."""
        if not self._entries:
            return
        
        if self._config.eviction_policy == EvictionPolicy.LRU:
            key = self._access_order.pop(0)
        elif self._config.eviction_policy == EvictionPolicy.LFU:
            key = min(self._entries.keys(), 
                     key=lambda k: self._entries[k].frequency)
        else:
            key = self._access_order.pop(0)
        
        if key in self._entries:
            del self._entries[key]
            self._stats.evictions += 1
    
    def _update_access_order(self, key: str) -> None:
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)


def test_cache():
    """Test cache functionality."""
    config = CacheConfig(max_size=3, eviction_policy=EvictionPolicy.LRU)
    cache = Cache(config)
    
    # Basic operations
    cache.put("key1", "value1")
    assert cache.get("key1") == "value1"
    
    # Eviction with LRU
    cache.put("key2", "value2")
    cache.put("key3", "value3")
    
    # Access key2 to make it recently used
    cache.get("key2")
    
    # key1 should be evicted (least recently used)
    cache.put("key4", "value4")
    
    assert cache.get("key1") is None  # evicted
    assert cache.get("key2") == "value2"  # still there
    assert cache.get("key4") == "value4"  # just added
    
    # Stats
    stats = cache.get_stats()
    assert stats.evictions >= 1
    
    # TTL
    config2 = CacheConfig(max_size=10, default_ttl=0.1)
    cache2 = Cache(config2)
    
    cache2.put("key1", "value1")
    assert cache2.get("key1") == "value1"
    
    time.sleep(0.2)
    assert cache2.get("key1") is None
    
    print("Tests passed")


if __name__ == "__main__":
    test_cache()
