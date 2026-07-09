# Agentic Security

Agentic Security provides a comprehensive defense framework against agentjacking attacks targeting AI coding agents and autonomous workflows. It implements workflow graph execution control, runtime protection, and provenance validation.

## Installation

```bash
pip install agentic-security
```

## Quick Start

### Python API

```python
from agentic_security import WorkflowGraphController

# Initialize controller
controller = WorkflowGraphController()

# Validate LLM-generated intent
intent = {
    "action": "read_file",
    "parameters": {
        "path": "/app/input/data.txt"
    }
}

result = controller.validate_intent(intent)

if result['is_valid']:
    # Execute the action
    output = controller.execute(intent)
else:
    print(f"Request blocked: {result['reason']}")
```

### Command Line

```bash
# Validate an intent
agentic-security validate '{"action": "read_file", "parameters": {"path": "/app/data.txt"}}'

# Run security tests
agentic-security test --verbose

# Scan environment for threats
agentic-security scan

# Simulate attack scenarios
agentic-security simulate --scenario=workspace_poisoning
```

## Features

- **Workflow Graph Execution Control**: Validates all LLM-generated tool requests against a graph of allowed actions
- **Local Runtime Protector**: Monitors execution environment for unauthorized system-level actions
- **SQL Injection Prevention**: Blocks destructive database queries and injection patterns
- **Provenance Validation**: Cryptographic signing for agent identity verification
- **Comprehensive Testing**: Built-in attack scenarios and defense validation

## Allowed Actions

The framework supports the following actions with strict parameter constraints:

1. **read_file**: Read file contents (restricted to authorized paths)
2. **write_file**: Write file contents (restricted to authorized directories)
3. **execute_script**: Run external scripts (only from approved directories)
4. **send_network_request**: HTTP/HTTPS requests (domain whitelist)
5. **db_query**: Database queries (SELECT only, no destructive operations)

## Configuration

```python
from agentic_security import WorkflowGraphController
import json

config = {
    "allowed_actions": ["read_file", "write_file", "execute_script", "send_network_request", "db_query"],
    "path_constraints": {
        "read_file": "^/app/.*$",
        "write_file": "^/app/output/.*$",
        "execute_script": "^/app/scripts/.*$"
    },
    "domain_whitelist": ["api.*.com", "trusted.*"],
    "sql_restrictions": {
        "allowed_verbs": ["SELECT"],
        "blocked_patterns": ["DROP", "DELETE", "UPDATE", "INSERT"]
    }
}

controller = WorkflowGraphController.from_config(config)
```

## Documentation

For detailed architecture, testing procedures, and API reference, see the full documentation:

- [Architecture](../docs/ARCHITECTURE.md)
- [Testing Guide](../docs/TESTING.md)
- [Contributing](../docs/CONTRIBUTING.md)

## Security Notice

This is a security tool. Use it responsibly to protect your AI systems from agentjacking attacks. All findings should be reported through responsible disclosure channels.

## License

MIT License - See LICENSE file for details.
