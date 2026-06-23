# WebSocket Frame Parser Implementation

## Complete Code

```python
from typing import Optional, List
from enum import Enum
from dataclasses import dataclass, field
import os
import struct


class WebSocketOpCode(Enum):
    """WebSocket opcodes per RFC 6455 Section 5.2."""
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA
    CONTINUATION = 0x0


@dataclass
class WebSocketFrame:
    """A single WebSocket frame.

    Attributes:
        fin: Whether this is the final fragment of a message.
        opcode: The frame's opcode.
        mask: 4-byte masking key if the frame is masked, else None.
        payload: The unmasked application payload bytes.
    """
    fin: bool
    opcode: WebSocketOpCode
    mask: Optional[bytes] = None
    payload: bytes = b""


class WebSocketProtocolError(Exception):
    """Raised when a frame violates the RFC 6455 protocol."""


def _apply_mask(data: bytes, mask: bytes) -> bytes:
    """Apply (or reverse) WebSocket XOR masking.

    Masking is symmetric: applying the same mask again reverses it.

    Args:
        data: The bytes to mask/unmask.
        mask: The 4-byte masking key.

    Returns:
        The masked/unmasked bytes.
    """
    return bytes(b ^ mask[i & 3] for i, b in enumerate(data))


class WebSocketFrameParser:
    """Parse WebSocket frames from raw bytes.

    The parser is stateful and supports streaming: bytes may arrive in
    arbitrary chunks. Bytes are buffered until at least one complete frame
    can be produced.
    """

    # Control frames must have payload length <= 125 (RFC 6455 5.5).
    _MAX_CONTROL_PAYLOAD = 125

    def __init__(self) -> None:
        self._buffer: bytes = b""
        self._partial_frame: Optional[dict] = None

    def feed(self, data: bytes) -> List[WebSocketFrame]:
        """Feed raw bytes and return any complete frames decoded.

        Args:
            data: Newly received raw bytes from the transport.

        Returns:
            A list of fully-parsed WebSocketFrame objects. May be empty if
            no complete frame is yet available.

        Raises:
            WebSocketProtocolError: If a frame violates protocol invariants.
        """
        self._buffer += data
        frames: List[WebSocketFrame] = []

        while True:
            frame = self._try_parse_one()
            if frame is None:
                break
            frames.append(frame)

        return frames

    def _try_parse_one(self) -> Optional[WebSocketFrame]:
        """Try to parse a single frame from the front of the buffer.

        Returns:
            A WebSocketFrame if a complete frame is available, else None.
            On success the consumed bytes are removed from the buffer.
        """
        buf = self._buffer
        n = len(buf)

        # Need at least 2 bytes for the minimal header.
        if n < 2:
            return None

        b0 = buf[0]
        b1 = buf[1]

        fin = bool(b0 & 0x80)
        rsv = b0 & 0x70  # RSV1-3
        opcode_val = b0 & 0x0F

        masked = bool(b1 & 0x80)
        length_indicator = b1 & 0x7F

        # RSV bits must be zero unless an extension negotiated them.
        if rsv != 0:
            raise WebSocketProtocolError(f"Reserved bits set: {rsv:#04x}")

        try:
            opcode = WebSocketOpCode(opcode_val)
        except ValueError as exc:
            raise WebSocketProtocolError(
                f"Unknown opcode: {opcode_val:#x}"
            ) from exc

        # Determine header length and payload length.
        offset = 2
        if length_indicator < 126:
            payload_len = length_indicator
        elif length_indicator == 126:
            if n < offset + 2:
                return None
            payload_len = struct.unpack(">H", buf[offset:offset + 2])[0]
            offset += 2
        else:  # 127
            if n < offset + 8:
                return None
            payload_len = struct.unpack(">Q", buf[offset:offset + 8])[0]
            offset += 8
            # Most significant bit of 64-bit length must be 0 (RFC 6455 5.2).
            if payload_len >> 63:
                raise WebSocketProtocolError("64-bit length MSB must be 0")

        # Control frame validation (RFC 6455 5.5).
        is_control = opcode in (
            WebSocketOpCode.CLOSE,
            WebSocketOpCode.PING,
            WebSocketOpCode.PONG,
        )
        if is_control:
            if payload_len > self._MAX_CONTROL_PAYLOAD:
                raise WebSocketProtocolError(
                    "Control frame payload too large"
                )
            if not fin:
                raise WebSocketProtocolError(
                    "Control frames must not be fragmented"
                )

        # Read mask key if present.
        mask: Optional[bytes] = None
        if masked:
            if n < offset + 4:
                return None
            mask = buf[offset:offset + 4]
            offset += 4

        # Read payload.
        total_needed = offset + payload_len
        if n < total_needed:
            return None  # Wait for more data.

        payload = buf[offset:total_needed]
        if mask is not None:
            payload = _apply_mask(payload, mask)

        # Consume the bytes from the buffer.
        self._buffer = buf[total_needed:]

        return WebSocketFrame(
            fin=fin,
            opcode=opcode,
            mask=mask,
            payload=payload,
        )

    def construct_frame(
        self,
        opcode: WebSocketOpCode,
        payload: bytes,
        is_masked: bool = False,
        fin: bool = True,
    ) -> bytes:
        """Construct a WebSocket frame as raw bytes.

        Args:
            opcode: The frame opcode.
            payload: The application payload (unmasked).
            is_masked: Whether to mask the frame (clients must mask).
            fin: Whether this is the final fragment.

        Returns:
            The fully-encoded frame bytes ready for transmission.

        Raises:
            WebSocketProtocolError: If control frame constraints are violated.
        """
        is_control = opcode in (
            WebSocketOpCode.CLOSE,
            WebSocketOpCode.PING,
            WebSocketOpCode.PONG,
        )
        if is_control and len(payload) > self._MAX_CONTROL_PAYLOAD:
            raise WebSocketProtocolError("Control frame payload too large")
        if is_control and not fin:
            raise WebSocketProtocolError(
                "Control frames must not be fragmented"
            )

        b0 = (0x80 if fin else 0x00) | (opcode.value & 0x0F)

        length = len(payload)
        header = bytearray([b0])

        mask_bit = 0x80 if is_masked else 0x00

        if length < 126:
            header.append(mask_bit | length)
        elif length <= 0xFFFF:
            header.append(mask_bit | 126)
            header += struct.pack(">H", length)
        else:
            header.append(mask_bit | 127)
            header += struct.pack(">Q", length)

        if is_masked:
            mask = os.urandom(4)
            header += mask
            payload = _apply_mask(payload, mask)

        return bytes(header) + payload


class WebSocketMessage:
    """Accumulates frames into a complete WebSocket message.

    A logical message may be fragmented across an initial data frame
    (TEXT/BINARY) followed by zero or more CONTINUATION frames, terminated
    by a frame with FIN set.

    Control frames (PING/PONG/CLOSE) are *not* part of message
    fragmentation and are returned immediately as their own message.
    """

    def __init__(self) -> None:
        self._frame_buffer: List[bytes] = []
        self._opcode: Optional[WebSocketOpCode] = None
        self._is_fin: bool = False

    def process_frame(
        self, frame: WebSocketFrame
    ) -> Optional["WebSocketMessage"]:
        """Process a frame, returning a completed message when finished.

        Args:
            frame: The next decoded frame.

        Returns:
            self if the message is now complete, otherwise None (more
            continuation frames expected).

        Raises:
            WebSocketProtocolError: On fragmentation protocol violations.
        """
        is_control = frame.opcode in (
            WebSocketOpCode.CLOSE,
            WebSocketOpCode.PING,
            WebSocketOpCode.PONG,
        )

        # Control frames are standalone and never fragmented.
        if is_control:
            if self._opcode is not None and not self._is_fin:
                # We were mid-fragment; control frame may interleave, but
                # it should be delivered as its own message instance.
                raise WebSocketProtocolError(
                    "Control frame must be handled separately during "
                    "fragmentation"
                )
            self._opcode = frame.opcode
            self._frame_buffer.append(frame.payload)
            self._is_fin = True
            return self

        if frame.opcode == WebSocketOpCode.CONTINUATION:
            if self._opcode is None:
                raise WebSocketProtocolError(
                    "CONTINUATION frame without an initial data frame"
                )
        else:  # TEXT or BINARY (start of a new message)
            if self._opcode is not None and not self._is_fin:
                raise WebSocketProtocolError(
                    "New data frame received before previous message "
                    "finished"
                )
            self._opcode = frame.opcode

        self._frame_buffer.append(frame.payload)

        if frame.fin:
            self._is_fin = True
            return self

        return None

    @property
    def opcode(self) -> Optional[WebSocketOpCode]:
        """The opcode of the (initial) data frame for this message."""
        return self._opcode

    @property
    def complete(self) -> bool:
        """Whether the message has received its final fragment."""
        return self._is_fin

    @property
    def payload(self) -> bytes:
        """The reassembled payload across all fragments."""
        return b"".join(self._frame_buffer)
```

## Usage Example

```python
if __name__ == "__main__":
    parser = WebSocketFrameParser()

    # Server constructs an unmasked text frame.
    raw = parser.construct_frame(WebSocketOpCode.TEXT, b"Hello")

    # Simulate streaming: feed it in two chunks.
    assert parser.feed(raw[:2]) == []          # incomplete
    frames = parser.feed(raw[2:])               # completes
    assert len(frames) == 1
    assert frames[0].payload == b"Hello"

    # Fragmented message reassembly.
    msg = WebSocketMessage()
    f1 = WebSocketFrame(fin=False, opcode=WebSocketOpCode.TEXT, payload=b"Hel")
    f2 = WebSocketFrame(
        fin=True, opcode=WebSocketOpCode.CONTINUATION, payload=b"lo"
    )
    assert msg.process_frame(f1) is None
    done = msg.process_frame(f2)
    assert done is not None and done.payload == b"Hello"

    # Masked client frame round-trip.
    masked = parser.construct_frame(
        WebSocketOpCode.BINARY, b"\x00\xff", is_masked=True
    )
    out = parser.feed(masked)
    assert out[0].payload == b"\x00\xff"  # unmasked transparently
    print("All checks passed.")
```

## Design Decisions & Tradeoffs

**Streaming buffer model.** `feed()` appends to an internal buffer and greedily extracts every complete frame. Returning `None` from `_try_parse_one` (rather than raising) when bytes are insufficient cleanly distinguishes *"need more data"* from *"protocol error"*. The header is re-parsed each call; this is simple and correct. A high-throughput implementation could cache the partially-parsed header in `self._partial_frame` to avoid rework on large payloads — I kept correctness/clarity over that micro-optimization.

**Symmetric masking.** XOR masking is its own inverse, so one `_apply_mask` helper serves both encoding and decoding. I used `i & 3` instead of `i % 4` as a minor speedup; for very large payloads a chunked `int.from_bytes` XOR would be faster, but the byte-wise version is clearest.

**Separation of frames vs. messages.** Per RFC 6455, *fragmentation* (FIN + CONTINUATION) is a message-level concern, while masking and length encoding are frame-level. I kept `WebSocketFrameParser` ignorant of message semantics and put reassembly in `WebSocketMessage`, matching the provided interface and keeping each class single-responsibility.

**Validation pushed early.** RSV bits, unknown opcodes, oversized/fragmented control frames, and the 64-bit MSB rule are all checked during parsing so callers fail fast with a typed `WebSocketProtocolError`.

## Edge Cases Handled

- **Partial headers/payloads** — frames split across multiple `feed()` calls (including mid-length-field and mid-mask-key) buffer correctly.
- **All three length encodings** — 7-bit (<126), 16-bit (126), and 64-bit (127), with the 64-bit MSB-zero requirement enforced.
- **Masked frames** — mask key extracted and payload transparently unmasked; `construct_frame` generates a cryptographically-random mask via `os.urandom`.
- **Control-frame constraints** — payload ≤ 125 bytes and `fin` must be true; violations raise.
- **Multiple frames per chunk** — the `while` loop drains all complete frames from one `feed`.
- **Fragmentation errors** — a `CONTINUATION` without a starter, or a new data frame mid-message, both raise.
- **Empty payloads** — zero-length frames (e.g., an empty PING) parse and round-trip fine.

A couple of items intentionally left to the caller: UTF-8 validation of TEXT payloads, and the interleaving of control frames *within* a fragmented data stream (RFC permits this, but it requires a higher-level dispatcher tracking two message contexts simultaneously).