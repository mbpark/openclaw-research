"""
Agent discovery and beacon management
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional
from .beacon import FieldBeacon

def discover_agents(workspace_path: Path = None) -> List[Dict]:
    """Discover all active agents in the field network"""
    if workspace_path is None:
        workspace_path = Path.home() / ".openclaw" / "workspace"
    
    field_network = workspace_path / "field_network"
    
    if not field_network.exists():
        return []
    
    agents = []
    for beacon_file in field_network.glob("field_beacon_*.json"):
        try:
            with open(beacon_file, 'r') as f:
                beacon_data = json.load(f)
            
            # Check if beacon is still valid
            beacon = FieldBeacon(**beacon_data)
            if beacon.is_valid():
                agents.append(beacon.to_dict())
        except json.JSONDecodeError:
            continue
    
    return agents

def find_by_capability(capability: str, workspace_path: Path = None) -> List[Dict]:
    """Find agents that support a specific capability"""
    agents = discover_agents(workspace_path)
    return [agent for agent in agents if capability in agent['capabilities']]

def refresh_beacons(workspace_path: Path = None):
    """Refresh all beacon timestamps"""
    if workspace_path is None:
        workspace_path = Path.home() / ".openclaw" / "workspace"
    
    field_network = workspace_path / "field_network"
    
    if not field_network.exists():
        return
    
    for beacon_file in field_network.glob("field_beacon_*.json"):
        try:
            with open(beacon_file, 'r') as f:
                beacon_data = json.load(f)
            
            # Update timestamp
            beacon_data['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            with open(beacon_file, 'w') as f:
                json.dump(beacon_data, f, indent=2)
        except json.JSONDecodeError:
            continue

def clean_stale_beacons(max_age_days: int = 7, workspace_path: Path = None):
    """Remove beacons older than specified days"""
    if workspace_path is None:
        workspace_path = Path.home() / ".openclaw" / "workspace"
    
    field_network = workspace_path / "field_network"
    
    if not field_network.exists():
        return
    
    current_time = datetime.now(timezone.utc)
    
    for beacon_file in field_network.glob("field_beacon_*.json"):
        try:
            with open(beacon_file, 'r') as f:
                beacon_data = json.load(f)
            
            timestamp = datetime.fromisoformat(beacon_data['timestamp'])
            age_days = (current_time - timestamp).total_seconds() / 86400
            
            if age_days > max_age_days:
                beacon_file.unlink()
        except (json.JSONDecodeError, KeyError):
            continue
