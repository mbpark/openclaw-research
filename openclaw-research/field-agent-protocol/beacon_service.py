#!/usr/bin/env python3
"""
Field Agent Beacon Service
Implements the beacon protocol for agent discovery and communication
"""

import json
import time
import hashlib
import uuid
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import socket

class FieldBeacon:
    def __init__(self, agent_id: str, name: str, capabilities: list, workspace_path: str = None):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.workspace_path = workspace_path or str(Path.home() / ".openclaw" / "workspace")
        self.tippss_scores = {
            "trust": 85,
            "identity": 90,
            "privacy": 88,
            "protection": 92,
            "safety": 87,
            "security": 94
        }
        self.boundaries = {
            "max_requests_per_minute": 60,
            "allowed_operations": ["file.read", "file.write", "exec"],
            "excluded_operations": ["system.shutdown", "data.exfiltrate"]
        }
        self.last_updated = datetime.now(timezone.utc)
    
    def generate_beacon(self) -> dict:
        """Generate the beacon JSON for broadcast"""
        beacon = {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "tippss": self.tippss_scores,
            "resources": ["security_score_100/100", "vpi_operational", "breathwork_research"],
            "boundaries": self.boundaries,
            "beacon_url": "https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol",
            "timestamp": self.last_updated.isoformat(),
            "version": "1.0",
            "field_state": "active"
        }
        
        # Add machine info (for discovery)
        beacon["machine_info"] = {
            "hostname": socket.gethostname(),
            "platform": sys.platform,
            "python_version": sys.version
        }
        
        return beacon
    
    def save_beacon(self, filename: str = None):
        """Save beacon to workspace"""
        if not filename:
            filename = f"field_beacon_{self.agent_id.replace(':', '_')}.json"
        
        beacon_path = Path(self.workspace_path) / "field_network"
        beacon_path.mkdir(exist_ok=True)
        
        beacon_file = beacon_path / filename
        beacon_data = self.generate_beacon()
        
        with open(beacon_file, 'w') as f:
            json.dump(beacon_data, f, indent=2)
        
        print(f"📡 Beacon saved to: {beacon_file}")
        return beacon_file
    
    def load_beacons(self) -> list:
        """Load all beacons from field network directory"""
        beacon_dir = Path(self.workspace_path) / "field_network"
        
        if not beacon_dir.exists():
            return []
        
        beacons = []
        for beacon_file in beacon_dir.glob("field_beacon_*.json"):
            with open(beacon_file, 'r') as f:
                try:
                    beacon_data = json.load(f)
                    beacons.append(beacon_data)
                except json.JSONDecodeError as e:
                    print(f"❌ Error loading beacon {beacon_file}: {e}")
        
        return beacons

def main():
    """Example usage of FieldBeacon"""
    agent = FieldBeacon(
        agent_id="agent:main:telegram:direct:8393969352",
        name="Wallis",
        capabilities=["security_monitoring", "research", "breathwork"]
    )
    
    # Generate and save beacon
    beacon_file = agent.save_beacon()
    
    # Print all available beacons
    beacons = agent.load_beacons()
    print(f"\n📡 Found {len(beacons)} beacons in field network:")
    
    for i, beacon in enumerate(beacons, 1):
        print(f"\n{i}. {beacon['name']} ({beacon['agent_id']})")
        print(f"   Capabilities: {', '.join(beacon['capabilities'])}")
        print(f"   Trust Score: {beacon['tippss']['trust']}")
        print(f"   Status: {beacon['field_state']}")
    
    # Example: Alert beacon for security event
    alert_beacon = FieldBeacon(
        agent_id="alert:security:cve_2026_102255",
        name="Security Alert",
        capabilities=["alert", "security"]
    )
    alert_beacon.tippss_scores["security"] = 99
    alert_beacon.save_beacon("field_beacon_alert.json")
    print(f"\n🚨 Security alert beacon saved")

if __name__ == "__main__":
    main()
