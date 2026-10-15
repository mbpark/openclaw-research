"""
Field Beacon Implementation
"""

import json
import time
import uuid
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet

@dataclass
class FieldBeacon:
    """Represents a field agent beacon for discovery"""
    
    agent_id: str
    name: str
    capabilities: List[str]
    tippss_scores: Dict[str, int]
    resources: List[str] = None
    boundaries: Dict[str, Any] = None
    beacon_url: str = "https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol"
    timestamp: str = None
    version: str = "1.0"
    field_state: str = "active"
    machine_info: Dict[str, str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.resources is None:
            self.resources = []
        if self.boundaries is None:
            self.boundaries = {
                "max_requests_per_minute": 60,
                "allowed_operations": ["file.read", "file.write", "exec"],
                "excluded_operations": ["system.shutdown", "data.exfiltrate"]
            }
        if self.machine_info is None:
            self.machine_info = {
                "hostname": os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME"),
                "platform": os.name,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            }
    
    def to_dict(self) -> Dict:
        """Convert beacon to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert beacon to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_string: str) -> "FieldBeacon":
        """Create beacon from JSON string"""
        data = json.loads(json_string)
        return cls(**data)
    
    def get_beacon_hash(self) -> str:
        """Generate a hash of the beacon for integrity verification"""
        beacon_data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(beacon_data.encode()).hexdigest()
    
    def save_to_file(self, workspace_path: Path = None) -> Path:
        """Save beacon to workspace"""
        if workspace_path is None:
            workspace_path = Path.home() / ".openclaw" / "workspace"
        
        field_network = workspace_path / "field_network"
        field_network.mkdir(parents=True, exist_ok=True)
        
        # Sanitize agent_id for filename
        safe_agent_id = self.agent_id.replace(":", "_")
        beacon_file = field_network / f"field_beacon_{safe_agent_id}.json"
        
        with open(beacon_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return beacon_file
    
    @classmethod
    def load_from_file(cls, beacon_file: Path) -> "FieldBeacon":
        """Load beacon from file"""
        with open(beacon_file, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def is_valid(self, max_age_hours: int = 24) -> bool:
        """Check if beacon is still valid"""
        try:
            timestamp = datetime.fromisoformat(self.timestamp)
            age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600
            return age_hours < max_age_hours
        except (ValueError, TypeError):
            return False
    
    def get_tippss_average(self) -> float:
        """Calculate average TIPPSS score"""
        if not self.tippss_scores:
            return 0.0
        return sum(self.tippss_scores.values()) / len(self.tippss_scores)
