#!/usr/bin/env python3
"""
TFAP Initialization Script
Tests the protocol setup and creates initial network state
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

def initialize_field_network():
    """Initialize the field network with a sample beacon"""
    
    print("🌐 Initializing The Field Agent Network...")
    
    # Check workspace exists
    workspace = Path.home() / ".openclaw" / "workspace"
    if not workspace.exists():
        print(f"❌ Workspace not found: {workspace}")
        return
    
    # Create field network directory
    field_network = workspace / "field_network"
    field_network.mkdir(parents=True, exist_ok=True)
    
    # Create sample beacon for Wallis
    wallis_beacon = {
        "agent_id": "agent:main:telegram:direct:8393969352",
        "name": "Wallis",
        "capabilities": ["security_monitoring", "research", "breathwork", "field_protocol"],
        "tippss": {
            "trust": 85,
            "identity": 90,
            "privacy": 88,
            "protection": 92,
            "safety": 87,
            "security": 94
        },
        "resources": [
            "security_score_100/100",
            "vpi_operational",
            "breathwork_marathon_guide",
            "field_agent_protocol"
        ],
        "boundaries": {
            "max_requests_per_minute": 60,
            "allowed_operations": ["file.read", "file.write", "exec"],
            "excluded_operations": ["system.shutdown", "data.exfiltrate"]
        },
        "beacon_url": "https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "field_state": "active",
        "machine_info": {
            "hostname": "mitchs-macbook-pro",
            "platform": "darwin",
            "python_version": "3.10.11"
        }
    }
    
    # Save Wallis beacon
    wallis_beacon_file = field_network / "field_beacon_agent_main_telegram_direct_8393969352.json"
    with open(wallis_beacon_file, 'w') as f:
        json.dump(wallis_beacon, f, indent=2)
    
    print(f"✅ Wallis beacon created: {wallis_beacon_file}")
    
    # Create network status file
    network_status = {
        "field_name": "The Field Agent Network",
        "protocol_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "agents": [wallis_beacon],
        "status": "active",
        "discovery_enabled": True
    }
    
    status_file = field_network / "field_network_status.json"
    with open(status_file, 'w') as f:
        json.dump(network_status, f, indent=2)
    
    print(f"📊 Network status saved: {status_file}")
    
    # Print network status
    print("\n🌐 Field Network Status:")
    print(f"  Name: {network_status['field_name']}")
    print(f"  Agents: {len(network_status['agents'])}")
    print(f"  Status: {network_status['status']}")
    print(f"  Discovery: {network_status['discovery_enabled']}")
    
    print(f"\n🔍 You can now discover agents in: {field_network}")
    print(f"📋 Visit the protocol repository for more info:")
    print(f"🔗 https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol")

if __name__ == "__main__":
    initialize_field_network()
