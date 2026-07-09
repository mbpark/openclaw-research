"""MCP Provenance Validator for Agentic Security."""

import hashlib
import hmac
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ProvenanceToken:
    """Represents a cryptographic provenance token."""
    agent_id: str
    timestamp: int
    nonce: str
    signature: str
    
    def verify(self, secret_key: str) -> bool:
        """Verify the token signature."""
        # Create expected signature
        message = f"{self.agent_id}:{self.timestamp}:{self.nonce}"
        expected_signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, self.signature)

class ProvenanceValidator:
    """Validates agent provenance and cryptographic signatures."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.secret_key = self.config.get("secret_key", "default_secret_key")
        self.valid_agents = self.config.get("valid_agents", {})
        
        # Token expiration time (in seconds)
        self.token_expiration = self.config.get("token_expiration", 3600)
    
    def generate_token(self, agent_id: str) -> ProvenanceToken:
        """Generate a cryptographic token for an agent."""
        timestamp = int(time.time())
        nonce = hashlib.sha256(f"{timestamp}{agent_id}".encode()).hexdigest()[:16]
        
        message = f"{agent_id}:{timestamp}:{nonce}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return ProvenanceToken(
            agent_id=agent_id,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature
        )
    
    def validate_token(self, token: ProvenanceToken) -> Dict[str, Any]:
        """Validate a provenance token."""
        current_time = int(time.time())
        
        # Check if token is expired
        if current_time - token.timestamp > self.token_expiration:
            return {
                "valid": False,
                "reason": "Token expired",
                "token": token
            }
        
        # Verify signature
        if not token.verify(self.secret_key):
            return {
                "valid": False,
                "reason": "Invalid signature",
                "token": token
            }
        
        # Check if agent is valid
        if token.agent_id not in self.valid_agents:
            return {
                "valid": False,
                "reason": "Unknown agent",
                "token": token
            }
        
        return {
            "valid": True,
            "agent_id": token.agent_id,
            "timestamp": token.timestamp,
            "reason": "Token valid"
        }
    
    def create_signed_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a signed request with provenance."""
        timestamp = int(time.time())
        nonce = hashlib.sha256(f"{timestamp}{request_data}".encode()).hexdigest()[:16]
        
        # Combine data for signing
        sign_data = f"{request_data['agent_id']}:{timestamp}:{nonce}:{request_data.get('action', '')}"
        
        signature = hmac.new(
            self.secret_key.encode(),
            sign_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "agent_id": request_data["agent_id"],
            "timestamp": timestamp,
            "nonce": nonce,
            "action": request_data.get("action", ""),
            "payload": request_data.get("payload", {}),
            "signature": signature
        }
    
    def verify_request(self, signed_request: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a signed request."""
        current_time = int(time.time())
        
        # Check timestamp
        if current_time - signed_request["timestamp"] > self.token_expiration:
            return {
                "valid": False,
                "reason": "Request expired",
                "timestamp": signed_request["timestamp"]
            }
        
        # Recreate signature
        sign_data = f"{signed_request['agent_id']}:{signed_request['timestamp']}:{signed_request['nonce']}:{signed_request.get('action', '')}"
        expected_signature = hmac.new(
            self.secret_key.encode(),
            sign_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        if not hmac.compare_digest(expected_signature, signed_request["signature"]):
            return {
                "valid": False,
                "reason": "Invalid signature",
                "expected": expected_signature,
                "provided": signed_request["signature"]
            }
        
        # Check agent validity
        if signed_request["agent_id"] not in self.valid_agents:
            return {
                "valid": False,
                "reason": "Unknown agent",
                "agent_id": signed_request["agent_id"]
            }
        
        return {
            "valid": True,
            "agent_id": signed_request["agent_id"],
            "timestamp": signed_request["timestamp"],
            "action": signed_request.get("action", ""),
            "reason": "Request verified"
        }
