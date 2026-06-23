---
# Checkpoint 3

**Decision:** ☐ Continue ☐ Adjust ☐ Stop

---

# Category 5: Real-World Edge Cases

## Task 5.1: Cursor-Based Pagination

**Description:**
Implement cursor-based pagination with opaque cursors that can't be manipulated.

**Interface:**
```python
from typing import List, Optional, TypeVar
from dataclasses import dataclass
import base64
import json
import time
import hmac
import secrets


@dataclass
class Page[T]:
    items: List[T]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    total: int


@dataclass
class CursorData:
    timestamp: float
    page_number: int
    last_id: int


class PaginationCursor:
    """
    Opaque cursor implementation with HMAC signature.
    """
    
    def __init__(self, secret_key: bytes = None):
        self._secret = secret_key or secrets.token_bytes(32)

    def create_cursor(self, data: CursorData) -> str:
        """Create opaque cursor from data."""
        raw = json.dumps(data.__dict__).encode()
        # Create HMAC signature
        sig = hmac.new(self._secret, raw).hexdigest()
        # Combine and base64 encode
        combined = base64.b64encode(raw + b":" + sig.encode())
        return combined.decode()

    def decode_cursor(self, cursor_str: str) -> Optional[CursorData]:
        """Decode and validate cursor."""
        try:
            decoded = base64.b64decode(cursor_str.encode()).decode()
            # Verify HMAC signature
            raw, sig = decoded.split(":")
            expected_sig = hmac.new(self._secret, raw.encode()).hexdigest()
            if sig != expected_sig:
                return None
            return CursorData(**json.loads(raw))
        except Exception:
            return None
```

**What to evaluate:**
- Cursor is opaque (encoded, not "page 3")
- HMAC signature prevents manipulation
- Efficient page retrieval (no rescan from start)
- Boundary condition handling
- Time complexity per page access

**Scoring:** __ / 6
