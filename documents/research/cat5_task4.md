## Task 5.5: Cache-Based Pagination with Cursor Support

**Description:**
Implement cursor-based pagination system with in-memory cache for large datasets.

**Key constraints:**
- Thousands of items, can't fit all in memory at once
- Serve pagination for hundreds of concurrent requests
- Cursors must be opaque (can't reverse-engineer position)
- Handle items being added/removed during pagination

**Interface:**
```python
from typing import List, Optional, TypeVar
from dataclasses import dataclass
import base64
import json
import time
import hmac
import secrets
import threading


@dataclass
class Page[T]:
    items: List[T]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    total: int  # approximate


@dataclass
class CursorState:
    timestamp: float
    offset: int
    direction: str  # "next" or "prev"


class CachePagingEngine:
    """
    Cached cursor-based pagination engine.
    """
    
    def __init__(
        self,
        items: List[T],
        max_page_size: int = 100
    ):
        self._items = items
        self._max_page_size = max_page_size
        self._secret = secrets.token_bytes(32)
        self._page_cache: dict = {}
        self._lock = threading.RLock()

    def _sign_cursor(self, state: CursorState) -> str:
        """Create opaque, signed cursor."""
        raw = json.dumps(state.__dict__).encode()
        sig = hmac.new(self._secret, raw).hexdigest()
        combined = base64.b64encode(raw + b":" + sig.encode())
        return combined.decode()

    def _decode_cursor(self, cursor_str: str) -> Optional[CursorState]:
        """Decode and validate cursor."""
        try:
            decoded = base64.b64decode(cursor_str.encode()).decode()
            raw, sig = decoded.split(":")
            expected_sig = hmac.new(self._secret, raw.encode()).hexdigest()
            if sig != expected_sig:
                return None
            return CursorState(**json.loads(raw))
        except Exception:
            return None

    def get_page(
        self,
        cursor: Optional[str] = None,
        page_size: int = 20
    ) -> Page[T]:
        """
        Get a page of items.
        
        - cursor=None: first page
        - cursor: continue from that position
        - Returns page with new cursors for navigation
        """
        with self._lock:
            page_size = min(page_size, self._max_page_size)
            
            if cursor is None:
                offset = 0
                prev_cursor = None
            else:
                state = self._decode_cursor(cursor)
                if not state:
                    raise ValueError("Invalid cursor")
                offset = state.offset
                if state.direction == "next":
                    prev_cursor = cursor
                else:
                    prev_cursor = None

            start = offset
            end = start + page_size
            items = self._items[start:end]

            next_cursor = None
            if end < len(self._items):
                next_state = CursorState(
                    timestamp=time.time(),
                    offset=end,
                    direction="next"
                )
                next_cursor = self._sign_cursor(next_state)

            return Page(
                items=items,
                next_cursor=next_cursor,
                prev_cursor=prev_cursor,
                total=len(self._items)
            )

    def add_item(self, item: T) -> None:
        """Add item to end."""
        with self._lock:
            self._items.append(item)

    def remove_item(self, item: T) -> bool:
        """Remove item."""
        with self._lock:
            try:
                self._items.remove(item)
                return True
            except ValueError:
                return False

    def total_count(self) -> int:
        """Return total count."""
        with self._lock:
            return len(self._items)
```

**What to evaluate:**
- Cursor is opaque (encoded, not "page 3")
- Efficient page retrieval (doesn't rescan from start)
- Cache works correctly across concurrent requests
- Handles boundary conditions (past end, before start)
- Page size enforcement
- Handles mutations during pagination gracefully
- Time complexity per page access

**Scoring:** __ / 6
