# HTTP Chunked Transfer Encoding

Here's a complete, robust implementation handling the full RFC 7230 chunked encoding spec.

```python
from typing import Optional, Iterator, List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """Represents a single chunk in chunked transfer encoding.

    Attributes:
        size: The declared size of the chunk in bytes.
        data: The raw chunk payload (length == size).
        trailing_headers: Optional trailer headers (only meaningful on the
            final/terminating chunk).
    """
    size: int
    data: bytes
    trailing_headers: Dict[str, str] = field(default_factory=dict)


class ChunkedParseError(Exception):
    """Raised when malformed chunked data is encountered."""


class ChunkedParser:
    """Incremental parser for HTTP chunked transfer encoding.

    Implements a streaming state machine so callers can feed arbitrary byte
    slices (partial chunks, multiple chunks, split CRLFs, etc.) and retrieve
    fully-formed chunks as they become available.

    Wire format (RFC 7230 §4.1):
        chunk          = chunk-size [ chunk-ext ] CRLF chunk-data CRLF
        last-chunk     = 1*("0") [ chunk-ext ] CRLF
        chunked-body   = *chunk last-chunk trailer-part CRLF
    """

    # State machine states
    _STATE_SIZE = "SIZE"        # reading the hex size line
    _STATE_DATA = "DATA"        # reading chunk payload
    _STATE_DATA_CRLF = "CRLF"   # consuming the CRLF after payload
    _STATE_TRAILER = "TRAILER"  # reading trailer headers after last-chunk
    _STATE_DONE = "DONE"        # terminal

    _CRLF = b"\r\n"
    _MAX_SIZE_LINE = 4096  # guard against unbounded buffering of a size line

    def __init__(self) -> None:
        self._buffer: bytes = b""
        self._expected_size: Optional[int] = None
        self._current_data: bytes = b""
        self._state: str = self._STATE_SIZE
        self._complete: bool = False
        self._ready: List[Chunk] = []
        self._trailers: Dict[str, str] = {}
        self._saw_last_chunk: bool = False

    @property
    def complete(self) -> bool:
        """True once the terminating chunk + trailers have been parsed."""
        return self._complete

    def feed(self, data: bytes) -> List[Chunk]:
        """Feed bytes into the parser and return any newly-completed chunks.

        Args:
            data: Arbitrary bytes from the stream. May contain zero, partial,
                one, or many chunks; chunk boundaries need not align.

        Returns:
            A list of fully-parsed Chunk objects (possibly empty).

        Raises:
            ChunkedParseError: On malformed input (bad hex size, oversized
                size line, or data fed after completion).
        """
        if self._complete and data:
            raise ChunkedParseError("data fed after chunked body completed")

        self._buffer += data
        self._run()

        ready, self._ready = self._ready, []
        return ready

    def get_chunk(self) -> Optional[Chunk]:
        """Pop the next available completed chunk, or None if none ready."""
        if self._ready:
            return self._ready.pop(0)
        return None

    # ------------------------------------------------------------------
    # Internal state machine
    # ------------------------------------------------------------------
    def _run(self) -> None:
        """Drive the state machine until no further progress is possible."""
        progressed = True
        while progressed and not self._complete:
            if self._state == self._STATE_SIZE:
                progressed = self._handle_size()
            elif self._state == self._STATE_DATA:
                progressed = self._handle_data()
            elif self._state == self._STATE_DATA_CRLF:
                progressed = self._handle_data_crlf()
            elif self._state == self._STATE_TRAILER:
                progressed = self._handle_trailer()
            else:  # DONE
                progressed = False

    def _read_line(self) -> Optional[bytes]:
        """Read one CRLF-terminated line from the buffer (without the CRLF).

        Returns None if no complete line is buffered yet.
        """
        idx = self._buffer.find(self._CRLF)
        if idx == -1:
            if len(self._buffer) > self._MAX_SIZE_LINE:
                raise ChunkedParseError("chunk header line too long")
            return None
        line = self._buffer[:idx]
        self._buffer = self._buffer[idx + 2:]
        return line

    def _handle_size(self) -> bool:
        line = self._read_line()
        if line is None:
            return False

        # Strip optional chunk extensions: "1a;name=value"
        size_token = line.split(b";", 1)[0].strip()
        if not size_token:
            raise ChunkedParseError("empty chunk size")

        try:
            size = int(size_token, 16)
        except ValueError as exc:
            raise ChunkedParseError(
                f"invalid hex chunk size: {size_token!r}"
            ) from exc

        if size < 0:
            raise ChunkedParseError("negative chunk size")

        self._expected_size = size
        self._current_data = b""

        if size == 0:
            # Last chunk: transition to trailer parsing.
            self._saw_last_chunk = True
            self._state = self._STATE_TRAILER
        else:
            self._state = self._STATE_DATA
        return True

    def _handle_data(self) -> bool:
        assert self._expected_size is not None
        needed = self._expected_size - len(self._current_data)
        available = self._buffer[:needed]
        self._current_data += available
        self._buffer = self._buffer[len(available):]

        if len(self._current_data) < self._expected_size:
            return False  # need more bytes

        self._state = self._STATE_DATA_CRLF
        return True

    def _handle_data_crlf(self) -> bool:
        if len(self._buffer) < 2:
            return False
        if self._buffer[:2] != self._CRLF:
            raise ChunkedParseError("missing CRLF after chunk data")
        self._buffer = self._buffer[2:]

        self._ready.append(
            Chunk(size=self._expected_size, data=self._current_data)
        )
        self._current_data = b""
        self._expected_size = None
        self._state = self._STATE_SIZE
        return True

    def _handle_trailer(self) -> bool:
        line = self._read_line()
        if line is None:
            return False

        if line == b"":
            # Blank line terminates trailers -> message complete.
            self._ready.append(
                Chunk(size=0, data=b"", trailing_headers=dict(self._trailers))
            )
            self._complete = True
            self._state = self._STATE_DONE
            return False

        # Parse a trailer header "Name: value"
        if b":" not in line:
            raise ChunkedParseError(f"malformed trailer header: {line!r}")
        name, value = line.split(b":", 1)
        self._trailers[name.strip().decode("latin-1")] = (
            value.strip().decode("latin-1")
        )
        return True


class ChunkedWriter:
    """Encoder for HTTP chunked transfer encoding."""

    _CRLF = b"\r\n"

    def begin(self) -> bytes:
        """Start chunked encoding (no preamble required)."""
        return b""

    def write_chunk(self, data: bytes) -> bytes:
        """Encode a single chunk.

        Format: ``<hex-size>CRLF<data>CRLF``

        Args:
            data: Raw payload bytes. An empty payload is skipped (returns b"")
                because a zero-size chunk would be interpreted as the
                terminator — use ``end()`` for that.

        Returns:
            The encoded chunk bytes.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not data:
            return b""  # never emit a stray "0\r\n\r\n" mid-stream
        size_hex = format(len(data), "X").encode("ascii")
        return size_hex + self._CRLF + data + self._CRLF

    def end(self, trailers: Optional[Dict[str, str]] = None) -> bytes:
        """Emit the terminating chunk and optional trailer headers."""
        out = b"0" + self._CRLF
        if trailers:
            for name, value in trailers.items():
                out += f"{name}: {value}".encode("latin-1") + self._CRLF
        out += self._CRLF
        return out

    def complete_message(self, *chunks: bytes) -> bytes:
        """Build a full chunked body from the given payloads."""
        result = self.begin()
        for chunk in chunks:
            result += self.write_chunk(chunk)
        return result + self.end()
```

## Design Decisions & Tradeoffs

**1. Explicit state machine over implicit buffer scanning.**
The parser uses named states (`SIZE → DATA → CRLF → ...`) rather than re-scanning the whole buffer each call. This makes partial-feed handling correct and O(n) amortized — each byte is consumed once. The tradeoff is more code, but streaming HTTP parsers *must* handle arbitrary split points.

**2. `write_chunk` operates on `bytes`, not `str`.**
The original stub did `data.decode()` — this breaks on binary payloads and reorders bytes through UTF-8. I kept a `str` convenience path but the canonical contract is bytes-in/bytes-out, since HTTP bodies are binary. The hex size is correctly uppercase via `format(n, "X")`.

**3. Empty-chunk guard.** `write_chunk(b"")` returns `b""` instead of `0\r\n\r\n`, preventing accidental premature stream termination.

**4. Trailers as first-class.** The final chunk surfaces `trailing_headers`, matching the `Chunk` dataclass contract and RFC 7230 trailer support.

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| Size line split across feeds (`"1` then `a\r\n"`) | Buffered until CRLF seen |
| Chunk data split mid-payload | Accumulated across feeds |
| CRLF after data split (`...data\r` then `\n`) | Waits for full CRLF |
| Chunk extensions (`1a;foo=bar`) | Stripped, size parsed correctly |
| Invalid hex / negative / empty size | Raises `ChunkedParseError` |
| Oversized size line (no CRLF) | Bounded, raises to prevent DoS |
| Data after completion | Raises error |
| Trailer headers + terminating blank line | Parsed and attached to final chunk |
| Missing CRLF after data | Raises error |

```python
# Round-trip sanity check
w = ChunkedWriter()
msg = w.complete_message(b"Wikipedia", b" in\r\n\r\n", b"chunks.")

p = ChunkedParser()
chunks = []
for byte in msg:              # feed one byte at a time — worst case
    chunks += p.feed(bytes([byte]))
assert b"".join(c.data for c in chunks if c.size) == b"Wikipedia in\r\n\r\nchunks."
assert p.complete
```

**Checkpoint 3 Decision: ☑ Continue** — core implementation is complete and robust; ready to proceed to Category 5 real-world edge cases (e.g. trailing-header injection defenses, max-body limits, connection-reset mid-chunk).