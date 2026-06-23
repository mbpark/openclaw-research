"""
Task 4.1: WebSocket Frame Parser

Implements WebSocket protocol frame parsing and handling.
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum


class WebSocketOpcode(Enum):
    CONTINUATION = 0x00
    TEXT = 0x01
    BINARY = 0x02
    CLOSE = 0x08
    PING = 0x09
    PONG = 0x0A


@dataclass
class WebSocketFrame:
    fin: bool = False
    rsv1: bool = False
    rsv2: bool = False
    rsv3: bool = False
    mask: bool = False
    opcode: WebSocketOpcode = WebSocketOpcode.TEXT
    payload: bytes = b""
    is_close: bool = False
    close_code: int = 1000
    close_reason: str = ""


class WebSocketFrameParser:
    """
    WebSocket frame parser implementation.
    Handles frame parsing according to RFC 6455.
    """
    
    def __init__(self):
        self._buffer = bytearray()
        self._frame_states = {
            'waiting_header': 0,
            'waiting_length': 1,
            'waiting_masking_key': 2,
            'waiting_payload': 3
        }
        self._current_state = self._frame_states['waiting_header']
        self._current_frame = None
    
    def add_data(self, data: bytes) -> List[WebSocketFrame]:
        """Add data to the parser and return completed frames."""
        self._buffer.extend(data)
        return self._parse_frames()
    
    def _parse_frames(self) -> List[WebSocketFrame]:
        """Parse frames from buffer."""
        completed_frames = []
        
        while len(self._buffer) >= 2:
            # Parse first two bytes
            first_byte = self._buffer[0]
            second_byte = self._buffer[1]
            
            # Parse control bits from first byte
            fin = bool(first_byte & 0x80)
            rsv1 = bool(first_byte & 0x40)
            rsv2 = bool(first_byte & 0x20)
            rsv3 = bool(first_byte & 0x10)
            opcode = first_byte & 0x0F
            
            # Parse second byte
            mask = bool(second_byte & 0x80)
            length = second_byte & 0x7F
            
            try:
                opcode = WebSocketOpcode(opcode)
            except ValueError:
                self._buffer = self._buffer[2:]
                continue
            
            # Initialize frame
            self._current_frame = WebSocketFrame()
            self._current_frame.fin = fin
            self._current_frame.rsv1 = rsv1
            self._current_frame.rsv2 = rsv2
            self._current_frame.rsv3 = rsv3
            self._current_frame.mask = mask
            self._current_frame.opcode = opcode
            
            if length < 126:
                # Short payload - payload directly follows masking key
                mask_offset = 4 if mask else 0
                total_length = 2 + mask_offset + length
                
                if len(self._buffer) >= total_length:
                    frame_data = self._buffer[:total_length]
                    self._complete_frame(frame_data, completed_frames)
                    self._buffer = self._buffer[total_length:]
            else:
                break
        
        return completed_frames
    
    def _complete_frame(self, data: bytes, frames: List[WebSocketFrame]):
        """Complete frame parsing."""
        frame = self._current_frame
        
        mask_offset = 2
        if frame.mask:
            mask_bytes = data[mask_offset:mask_offset + 4]
            mask_offset += 4
        
        payload = data[mask_offset:]
        frame.payload = payload
        
        if frame.opcode == WebSocketOpcode.CLOSE:
            frame.is_close = True
            if len(payload) >= 2:
                frame.close_code = int.from_bytes(payload[:2], 'big')
                if len(payload) > 2:
                    try:
                        frame.close_reason = payload[2:].decode('utf-8')
                    except UnicodeDecodeError:
                        pass
        
        frames.append(frame)
    
    def is_ready(self) -> bool:
        """Check if more data is needed."""
        return len(self._buffer) < 2


def create_text_frame(text: str) -> bytes:
    """Helper to create a simple text frame."""
    payload = text.encode('utf-8')
    first_byte = 0x80 | WebSocketOpcode.TEXT.value  # FIN + TEXT opcode
    second_byte = len(payload)  # Just length, no mask
    return bytes([first_byte, second_byte]) + payload


def test_websocket_parser():
    """Test WebSocket frame parser."""
    parser = WebSocketFrameParser()
    
    # Test simple text frame
    frame = create_text_frame("Hello WebSocket")
    result_frames = parser.add_data(frame)
    
    assert len(result_frames) == 1
    assert result_frames[0].opcode == WebSocketOpcode.TEXT
    assert result_frames[0].payload == b"Hello WebSocket"
    
    print("Tests passed")

if __name__ == "__main__":
    test_websocket_parser()
