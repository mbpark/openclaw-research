"""
Task 4.2: HTTP Chunked Transfer Encoding

Implements HTTP chunked transfer encoding handling.
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class TransferState(Enum):
    WAITING_LENGTH = "waiting_length"
    READING_PAYLOAD = "reading_payload"
    COMPLETE = "complete"
    ERROR = "error"


class ChunkedTransferEncoder:
    """Encodes data into HTTP chunked transfer format."""
    
    def encode_chunk(self, data: bytes) -> bytes:
        """Encode a chunk of data."""
        if not data:
            return b"0\r\n"
        
        length = len(data)
        return f"{length:x}\r\n".encode() + data + b"\r\n"
    
    def encode_chunks(self, chunks: List[bytes]) -> bytes:
        """Encode multiple chunks."""
        output = bytearray()
        for chunk in chunks:
            output.extend(self.encode_chunk(chunk))
        output.extend(b"0\r\n")
        return bytes(output)


class ChunkedTransferDecoder:
    """Decodes HTTP chunked transfer format."""
    
    def __init__(self):
        self._buffer = bytearray()
        self._state = TransferState.WAITING_LENGTH
        self._chunk_length: int = -1
        self._current_chunk: bytearray = None
        self._collected_chunks: List[bytes] = []
    
    def add_data(self, data: bytes) -> bool:
        """Add data and return True if complete."""
        self._buffer.extend(data)
        
        while self._state != TransferState.COMPLETE and self._state != TransferState.ERROR:
            if self._state == TransferState.WAITING_LENGTH:
                crlf_pos = self._buffer.find(b"\r\n")
                if crlf_pos == -1:
                    break
                
                length_str = self._buffer[:crlf_pos].decode('ascii')
                self._buffer = self._buffer[crlf_pos + 2:]
                
                try:
                    self._chunk_length = int(length_str, 16)
                except ValueError:
                    self._state = TransferState.ERROR
                    return True
                
                if self._chunk_length == 0:
                    self._state = TransferState.COMPLETE
                    return True
                
                self._current_chunk = bytearray()
                self._state = TransferState.READING_PAYLOAD
            
            else:  # READING_PAYLOAD
                if len(self._buffer) < self._chunk_length:
                    break
                
                chunk_data = self._buffer[:self._chunk_length]
                self._buffer = self._buffer[self._chunk_length:]
                
                # Remove trailing CRLF
                if len(self._buffer) >= 2 and self._buffer[:2] == b"\r\n":
                    self._buffer = self._buffer[2:]
                
                self._collected_chunks.append(bytes(chunk_data))
                self._state = TransferState.WAITING_LENGTH
        
        return self._state == TransferState.COMPLETE
    
    def get_collected_chunks(self) -> List[bytes]:
        return self._collected_chunks.copy()
    
    def is_complete(self) -> bool:
        return self._state == TransferState.COMPLETE
    
    def reset(self):
        self._buffer = bytearray()
        self._state = TransferState.WAITING_LENGTH
        self._chunk_length = -1
        self._current_chunk = None
        self._collected_chunks = []


def test_chunked_encoding():
    """Test HTTP chunked transfer encoding."""
    encoder = ChunkedTransferEncoder()
    decoder = ChunkedTransferDecoder()
    
    # Test encoding
    test_chunks = [b"Hello", b"World"]
    encoded = encoder.encode_chunks(test_chunks)
    
    # Decode
    decoder.add_data(encoded)
    collected = decoder.get_collected_chunks()
    
    assert len(collected) == 2
    for original, collected_chunk in zip(test_chunks, collected):
        assert original == collected_chunk
    
    assert decoder.is_complete()
    
    # Test error handling
    decoder.reset()
    decoder.add_data(b"Invalid\r\n")
    assert decoder._state == TransferState.ERROR
    
    print("Tests passed")

if __name__ == "__main__":
    test_chunked_encoding()