"""
Agent Setup and Configuration
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, List
import getpass

from .beacon import FieldBeacon

def setup_field_agent() -> FieldBeacon:
    """Interactive setup for a new field agent"""
    
    print("🔧 Setting up agent for The Field Agent Protocol (TFAP)...")
    
    # Get agent configuration
    agent_id = input("Agent ID (e.g., agent:main:telegram:direct:8393969352): ").strip()
    agent_name = input("Agent Name: ").strip()
    
    if not agent_id or not agent_name:
        print("❌ Agent ID and Name are required.")
        sys.exit(1)
    
    # Get capabilities
    capabilities_str = input("Capabilities (comma-separated): ").strip()
    capabilities = [cap.strip() for cap in capabilities_str.split(',')] if capabilities_str else []
    capabilities = [cap for cap in capabilities if cap]  # Remove empty strings
    
    # Create workspace and field network directory
    workspace_path = Path.home() / ".openclaw" / "workspace"
    field_network = workspace_path / "field_network"
    field_network.mkdir(parents=True, exist_ok=True)
    
    # Initialize agent configuration with default TIPPSS scores
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
    beacon = FieldBeacon(
        agent_id=agent_id,
        name=agent_name,
        capabilities=capabilities,
        tippss_scores=agent_config["tippss_scores"],
        resources=["security_score_100/100", "vpi_operational"],
        boundaries=agent_config["boundaries"],
        beacon_url=agent_config["beacon_url"],
        timestamp=datetime.now(timezone.utc).isoformat(),
        field_state="active"
    )
    
    beacon_file = beacon.save_to_file(workspace_path)
    print(f"📡 Initial beacon saved to: {beacon_file}")
    
    # Create agent instance file
    instance_file = create_agent_instance(agent_config, workspace_path)
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
    
    return beacon

def load_agent_config(workspace_path: Path = None) -> Dict:
    """Load agent configuration from workspace"""
    if workspace_path is None:
        workspace_path = Path.home() / ".openclaw" / "workspace"
    
    config_file = workspace_path / "agent_config.json"
    
    if not config_file.exists():
        print(f"❌ Agent configuration not found: {config_file}")
        return None
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return config

def create_agent_instance(agent_config: Dict, workspace_path: Path) -> Path:
    """Create Python agent instance file"""
    
    agent_name = agent_config["name"]
    agent_id = agent_config["agent_id"]
    capabilities = agent_config["capabilities"]
    
    class_name = "".join(part.capitalize() for part in agent_name.split()) + "Agent"
    
    instance_code = f'''#!/usr/bin/env python3
"""
{agent_name} - TFAP Agent Instance
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

from field_agent_protocol.beacon import FieldBeacon

class {class_name}:
    """Field Agent for {agent_name}"""
    
    def __init__(self):
        self.agent_id = "{agent_id}"
        self.name = "{agent_name}"
        self.capabilities = {json.dumps(capabilities)}
        self.workspace_path = Path.home() / ".openclaw" / "workspace"
        self.field_network = self.workspace_path / "field_network"
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load agent configuration"""
        config_file = self.workspace_path / "agent_config.json"
        if not config_file.exists():
            return {{}}
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def get_beacon(self) -> Dict:
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
            "field_state": "active",
            "machine_info": {{
                "hostname": os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME"),
                "platform": os.name,
                "python_version": f"{{sys.version_info.major}}.{{sys.version_info.minor}}.{{sys.version_info.micro}}"
            }}
        }}
    
    def handle_request(self, request: Dict) -> Dict:
        """Process incoming requests"""
        # Implement request handling logic
        pass
    
    def broadcast_status(self):
        """Broadcast status to field network"""
        # Implement status broadcasting
        pass
    
    def get_tippss_scores(self) -> Dict:
        """Return current TIPPSS scores"""
        return {{
            "trust": 85,
            "identity": 90,
            "privacy": 88,
            "protection": 92,
            "safety": 87,
            "security": 94
        }}

if __name__ == "__main__":
    agent = {class_name}()
    print(f"🤖 {{agent.name}} initialized")
    print(f"📡 Agent ID: {{agent.agent_id}}")
    print(f"✨ Capabilities: {{', '.join(agent.capabilities)}}")
    
    # Save beacon
    beacon = agent.get_beacon()
    beacon_file = agent.field_network / f"field_beacon_{{agent.agent_id.replace(':', '_')}}.json"
    with open(beacon_file, 'w') as f:
        json.dump(beacon, f, indent=2)
    print(f"📡 Beacon saved: {{beacon_file}}")
'''
    
    instance_file = workspace_path / f"agent_instance_{agent_id.replace(':', '_')}.py"
    
    with open(instance_file, 'w') as f:
        f.write(instance_code)
    
    # Make executable
    instance_file.chmod(0o755)
    
    return instance_file
