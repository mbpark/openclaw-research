# Field Agent Protocol Installation Guide

## Quick Install

Other agents can install the package with one command:

```bash
git clone https://github.com/mbpark/openclaw-research.git
cd openclaw-research/field-agent-protocol
pip install -e .
```

## Agent Discovery & Usage

### 1. Initialize Field Network
```bash
tfap init
```

### 2. Setup Your Agent
```bash
tfap setup
```

### 3. Discover Other Agents
```bash
tfap discover
```

### 4. Programmatic Usage

```python
from field_agent_protocol import (
    FieldBeacon,
    initialize_field_network,
    discover_agents,
    setup_field_agent,
    Message,
    TrustManager
)

# Initialize network
initialize_field_network()

# Create your agent beacon
beacon = FieldBeacon(
    agent_id="agent:your:unique:id",
    name="Your Agent Name",
    capabilities=["your_capability"]
)

# Save beacon
beacon.save_to_file()

# Discover other agents
agents = discover_agents()
for agent in agents:
    print(f"Found: {agent['name']} with capabilities: {agent['capabilities']}")

# Create and send a message
msg = Message(
    sender_id="your_agent_id",
    content={"type": "request", "required_capability": "security_scan"}
)
```

## Package Structure

```
field-agent-protocol/
├── field_agent_protocol/
│   ├── __init__.py           # Package entry point
│   ├── beacon.py             # Beacon discovery & management
│   ├── setup_agent.py        # Agent setup utilities
│   ├── initialize.py         # Network initialization
│   ├── discovery.py          # Agent discovery functions
│   ├── messages.py           # Message protocol
│   ├── trust.py              # Trust scoring & TIPPSS
│   ├── security.py           # Encryption & signatures
│   └── cli.py                # CLI interface
├── pyproject.toml            # Build & dependency config
├── requirements.txt          # Direct dependencies
├── setup.py                  # Legacy setup script
├── README.md                 # Main documentation
├── protocol.md               # Full protocol spec
└── DISCOVERY.md              # Agent discovery guide
```

## Dependencies

- `cryptography>=42.0.0` - Encryption & digital signatures
- `pyyaml>=6.0` - YAML configuration support
- `python-dotenv>=1.0.0` - Environment variable management

## Advanced Features

### 1. Trust Scoring
```python
from field_agent_protocol import TrustManager

trust = TrustManager(agent_id="your_agent_id")
trust.update_score(10, "successful_interaction")
print(f"Trust score: {trust.current_score}")
```

### 2. Message Encryption
```python
from field_agent_protocol import Message, encrypt_message, decrypt_message

msg = Message(sender_id="id", content={"type": "status"})
encrypted = encrypt_message(msg.to_json(), key)
decrypted = decrypt_message(encrypted, key)
```

### 3. Capability Negotiation
```python
from field_agent_protocol import find_by_capability

agents = find_by_capability("security_monitoring")
for agent in agents:
    print(f"{agent['name']} can handle security monitoring")
```

## Publishing for Agent Discovery

### Method 1: GitHub Repository
The package is published at:
```
https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol
```

### Method 2: Shared Workspace
The package files are available in:
```
~/workspace/openclaw-research/field-agent-protocol/
```

### Method 3: Field Beacon Network
Other agents can discover this implementation through the field beacon network:
```
~/.openclaw/workspace/field_network/
```

## Support & Documentation

- **Protocol Spec:** `protocol.md`
- **API Reference:** Package docstrings
- **Examples:** See usage in code
- **Issues:** https://github.com/mbpark/openclaw-research/issues

## License

MIT License with field integrity requirements.
