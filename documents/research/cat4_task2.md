```

**What to evaluate:**
- Correct frame header parsing
- Continuation frame reassembly
- Close/ping/pong frame handling
- Masked frame support

**Scoring:** __ / 6

---

## Task 4.2: HTTP Chunked Transfer Encoding

**Description:**
Implement chunked transfer encoding parser and writer.

**Interface:**
```python
from typing import Optional, Iterator
from dataclasses import dataclass


@dataclass
class Chunk:
    size: int
    data: bytes
    trailing_headers: dict = None


class ChunkedParser:
    """Parse chunked transfer encoding from stream."""
    
    def __init__(self):
        self._buffer: bytes = b""
        self._expected_size: Optional[int] = None
        self._current_chunk: Optional[Chunk] = None
        self._complete: bool = False

    def feed(self, data: bytes) -> List[Chunk]:
        """Feed data and return complete chunks."""
        ...

    def get_chunk(self) -> Optional[Chunk]:
        """Get next complete chunk."""
        ...


class ChunkedWriter:
    """Write chunked transfer encoding."""
    
    def begin(self) -> bytes:
        """Start chunked encoding (no special data needed)."""
        return b""

    def write_chunk(self, data: bytes) -> bytes:
        """
        Encode a chunk.
        Format: size(hex) CRLF data CRLF
        """
        size_hex = format(len(data), 'X')
        return f"{size_hex}\r\n{data.decode()}\r\n".encode()

    def end(self) -> bytes:
        """End chunked encoding with final chunk."""
        return "0\r\n\r\n".encode()

    def complete_message(self, *chunks: bytes) -> bytes:
        """Create complete chunked message."""
        result = self.begin()
        for chunk in chunks:
            result += self.write_chunk(chunk)
        return result + self.end()
```

**What to evaluate:**
- Correct chunk size encoding (hexadecimal, uppercase)
- Proper CRLF handling
- Complete parsing state machine
- Boundary condition handling

**Scoring:** __ / 6
