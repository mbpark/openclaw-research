"""
Message handling and communication protocol
"""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict

from .security import encrypt_message, decrypt_message, verify_signature, generate_key

@dataclass
class Message:
    """Standard message format for agent communication"""
    
    message_id: str = None
    timestamp: str = None
    sender_id: str = ""
    recipient_id: str = "all"
    priority: str = "normal"
    field_state: Dict = None
    content: Dict = None
    signature: str = None
    encryption: str = "aes-256-gcm"
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.field_state is None:
            self.field_state = {}
        if self.content is None:
            self.content = {}
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_string: str) -> "Message":
        """Create message from JSON string"""
        data = json.loads(json_string)
        return cls(**data)
    
    def add_signature(self, private_key: bytes) -> str:
        """Add digital signature to message"""
        message_data = json.dumps(self.to_dict(), sort_keys=True)
        self.signature = generate_key(message_data, private_key)
        return self.signature
    
    def sign(self, private_key: bytes) -> str:
        """Alias for add_signature"""
        return self.add_signature(private_key)
    
    def verify_signature(self, public_key: bytes) -> bool:
        """Verify message signature"""
        message_data = json.dumps(self.to_dict(), sort_keys=True)
        return verify_signature(message_data, self.signature, public_key)
    
    def encrypt(self, key: bytes) -> bytes:
        """Encrypt message with key"""
        return encrypt_message(self.to_json(), key)
    
    @classmethod
    def decrypt(cls, encrypted_data: bytes, key: bytes) -> "Message":
        """Decrypt message with key"""
        decrypted_json = decrypt_message(encrypted_data, key)
        return cls.from_json(decrypted_json)
    
    def is_valid(self, max_age_minutes: int = 60) -> bool:
        """Check if message is still valid"""
        try:
            timestamp = datetime.fromisoformat(self.timestamp)
            age_minutes = (datetime.now(timezone.utc) - timestamp).total_seconds() / 60
            return age_minutes < max_age_minutes
        except (ValueError, TypeError):
            return False

class MessageHandler:
    """Handles message routing and processing"""
    
    def __init__(self, agent_id: str, workspace_path=None):
        self.agent_id = agent_id
        self.workspace_path = workspace_path or Path.home() / ".openclaw" / "workspace"
        self.message_queue = []
        self.processed_messages = set()
    
    def handle_incoming(self, message: Message) -> bool:
        """Process incoming message"""
        if not message.is_valid():
            return False
        
        message_id = message.message_id
        if message_id in self.processed_messages:
            return False
        
        self.processed_messages.add(message_id)
        
        # Process based on message type
        content_type = message.content.get("type", "status")
        
        if content_type == "request":
            return self.handle_request(message)
        elif content_type == "response":
            return self.handle_response(message)
        elif content_type == "alert":
            return self.handle_alert(message)
        elif content_type == "status":
            return self.handle_status(message)
        elif content_type == "handshake":
            return self.handle_handshake(message)
        
        return False
    
    def handle_request(self, message: Message) -> bool:
        """Handle capability request"""
        required_cap = message.content.get("required_capability")
        # Implement request handling logic
        return True
    
    def handle_response(self, message: Message) -> bool:
        """Handle request response"""
        original_id = message.content.get("original_request_id")
        # Implement response handling logic
        return True
    
    def handle_alert(self, message: Message) -> bool:
        """Handle security alert"""
        severity = message.content.get("severity")
        source = message.content.get("source")
        # Implement alert handling logic
        return True
    
    def handle_status(self, message: Message) -> bool:
        """Handle status update"""
        # Implement status update logic
        return True
    
    def handle_handshake(self, message: Message) -> bool:
        """Handle agent handshake"""
        welcome = message.content.get("welcome_message")
        protocol_version = message.content.get("protocol_version")
        # Implement handshake logic
        return True
    
    def broadcast_message(self, message: Message):
        """Broadcast message to field network"""
        message.recipient_id = "all"
        # Implement broadcast logic
        pass
    
    def send_message(self, message: Message, recipient_id: str):
        """Send message to specific agent"""
        message.recipient_id = recipient_id
        # Implement send logic
        pass
    
    def queue_message(self, message: Message):
        """Queue message for later processing"""
        self.message_queue.append(message)
    
    def process_queue(self):
        """Process queued messages"""
        while self.message_queue:
            message = self.message_queue.pop(0)
            self.handle_incoming(message)
