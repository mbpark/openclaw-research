#!/usr/bin/env python3
"""
Field Agent Setup Script
Initializes an agent for The Field Agent Protocol
"""

import json
import os
import uuid
import hashlib
from pathlib import Path
from datetime import datetime, timezone

def setup_field_agent():
    """Setup a new agent for TFAP"""
    
    print("🔧 Setting up agent for The Field Agent Protocol (TFAP)...")
    
    # Get agent configuration
    agent_id = input("Agent ID (e.g., agent:main:telegram:direct:8393969352): ").strip()
    agent_name = input("Agent Name: ").strip()
    capabilities = input("Capabilities (comma-separated): ").strip().split(',')
    capabilities = [cap.strip() for cap in capabilities if cap.strip()]
    
    if not agent_id or not agent_name:
        print("❌ Agent ID and Name are required.")
        return
    
    # Create field network directory
    workspace_path = Path.home() / ".openclaw" / "workspace"
    field_network = workspace_path / "field_network"
    field_network.mkdir(parents=True, exist_ok=True)
    
    # Initialize agent configuration
    agent_config = {
        "agent_id": agent_id,
        "name": agent_name,
        "capabilities": capabilities,
        "tippss_scores": {
            "trust": 85,
            "identity": 90,
            "privacy": 88,
            "protection": 92,
            "safety": 87,
            "security": 94
        },
        "boundaries": {
            "max_requests_per_minute": 60,
            "allowed_operations": ["file.read", "file.write", "exec"],
            "excluded_operations": ["system.shutdown", "data.exfiltrate"]
        },
        "beacon_url": "https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol",
        "setup_timestamp": datetime.now(timezone.utc).isoformat(),
        "field_service_commitment": True
    }
    
    # Save agent configuration
    config_file = workspace_path / "agent_config.json"
    with open(config_file, 'w') as f:
        json.dump(agent_config, f, indent=2)
    
    print(f"✅ Agent configuration saved to: {config_file}")
    
    # Generate initial beacon
    beacon = generate_beacon(agent_config)
    beacon_file = field_network / f"field_beacon_{agent_id.replace(':', '_')}.json"
    with open(beacon_file, 'w') as f:
        json.dump(beacon, f, indent=2)
    
    print(f"📡 Initial beacon saved to: {beacon_file}")
    
    # Create agent instance file
    instance_file = field_network / f"agent_instance_{agent_id.replace(':', '_')}.py"
    instance_template = f'''#!/usr/bin/env python3
"""
{agent_name} - TFAP Agent Instance
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

class {agent_name.replace(' ', '')}Agent:
    """Field Agent for {agent_name}"""
    
    def __init__(self):
        self.agent_id = "{agent_id}"
        self.name = "{agent_name}"
        self.capabilities = {json.dumps(capabilities)}
        self.workspace_path = Path.home() / ".openclaw" / "workspace"
        self.field_network = self.workspace_path / "field_network"
    
    def get_beacon(self):
        """Return current beacon data"""
        return {{
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "tippss": {{
                "trust": 85,
                "identity": 90,
                "privacy": 88,
                "protection": 92,
                "safety": 87,
                "security": 94
            }},
            "resources": ["security_score_100/100", "vpi_operational"],
            "boundaries": {{
                "max_requests_per_minute": 60,
                "allowed_operations": ["file.read", "file.write", "exec"],
                "excluded_operations": ["system.shutdown", "data.exfiltrate"]
            }},
            "beacon_url": "https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "field_state": "active"
        }}
    
    def handle_request(self, request):
        """Process incoming requests"""
        # Implement request handling logic
        pass
    
    def broadcast_status(self):
        """Broadcast status to field network"""
        # Implement status broadcasting
        pass

if __name__ == "__main__":
    agent = {agent_name.replace(' ', '')}Agent()
    print(f"🤖 {agent.name} initialized")
    print(f"📡 Agent ID: {agent.agent_id}")
    print(f"✨ Capabilities: {{', '.join(agent.capabilities)}}")
'''
    
    with open(instance_file, 'w') as f:
        f.write(instance_template)
    
    print(f"🤖 Agent instance created: {instance_file}")
    
    # Print setup summary
    print("\n📋 Setup Summary:")
    print(f"  Agent ID: {agent_id}")
    print(f"  Name: {agent_name}")
    print(f"  Capabilities: {', '.join(capabilities)}")
    print(f"  Configuration: {config_file}")
    print(f"  Instance: {instance_file}")
    print(f"  Beacon: {beacon_file}")
    print(f"\n🚀 Agent ready for The Field!")

def generate_beacon(config):
    """Generate beacon JSON from config"""
    return {
        "agent_id": config["agent_id"],
        "name": config["name"],
        "capabilities": config["capabilities"],
        "tippss": config["tippss_scores"],
        "resources": ["security_score_100/100", "vpi_operational"],
        "boundaries": config["boundaries"],
        "beacon_url": config["beacon_url"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "field_state": "active"
    }

if __name__ == "__main__":
    setup_field_agent()
