# Category 4: Protocol Implementation

## Task 4.1: WebSocket Frame Parser

**Description:**
Implement WebSocket frame parsing per RFC 6455.

**Interface:**
```python
from typing import Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass


class WebSocketOpCode(Enum):
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA
    CONTINUATION = 0x0


@dataclass
class WebSocketFrame:
    fin: bool
    opcode: WebSocketOpCode
    mask: Optional[bytes] = None
    payload: bytes = b""


class WebSocketFrameParser:
    """Parse WebSocket frames from raw bytes."""
    
    def __init__(self):
        self._buffer: bytes = b""
        self._partial_frame: Optional[dict] = None
    
    def feed(self, data: bytes) -> List[WebSocketFrame]:
        """Feed raw bytes and return complete frames."""
        ...
    
    def construct_frame(
        self,
        opcode: WebSocketOpCode,
        payload: bytes,
        is_masked: bool = False
    ) -> bytes:
        """Construct a WebSocket frame."""
        ...


class WebSocketMessage:
    """
    Complete WebSocket message (may span multiple frames).
    """
    def __init__(self):
        self._frame_buffer: List[bytes] = []
        self._opcode: Optional[WebSocketOpCode] = None
        self._is_fin: bool = False

    def process_frame(self, frame: WebSocketFrame) -> Optional['WebSocketMessage']:
        """
        Process a frame and return complete message if done.
        """
        ...

    @property
    def complete(self) -> bool:
        return self._is_fin

    @property
    def payload(self) -> bytes:
        return b"".join(self._frame_buffer)
