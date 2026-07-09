# OpenClaw Security Packages

This directory contains production-ready Python packages for AI security tools developed in the OpenClaw Research repository.

## Packages

### 1. vlmguard

**Visual Prompt Injection Defense System**

A comprehensive defense system against Visual Prompt Injection (VPI) attacks.

**Features:**
- SVD-based maliciousness estimation
- SmoothVLM randomized smoothing
- R1 prompt rewriting
- Real-time scanning and protection

**Usage:**
```python
from vlmguard import VLMGuard
vlmguard = VLMGuard()
result = vlmguard.scan(input_text)
```

**CLI:**
```bash
vlmguard scan "Your input" --threshold 0.7
```

### 2. agentic-security

**Agentjacking Defense Framework**

Complete defense framework for AI coding agents and autonomous workflows.

**Features:**
- Workflow graph execution control
- Local runtime protection
- SQL injection prevention
- Provenance validation

**Usage:**
```python
from agentic_security import WorkflowGraphController
controller = WorkflowGraphController()
result = controller.validate_intent(intent_json)
```

**CLI:**
```bash
agentic-security validate '{"action": "read_file", "parameters": {"path": "/app/data.txt"}}'
```

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

**Quick Start:**
```bash
# Install from source
cd vlmguard && pip install -e .
cd agentic-security && pip install -e .
```

## Documentation

- [VLMGuard Documentation](../docs/README.md)
- [Agentic Security Documentation](../docs/ARCHITECTURE.md)
- [Testing Guide](../docs/TESTING.md)

## Contributing

See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - See [LICENSE](../LICENSE) file for details.

## Research Repository

These packages are developed as part of the OpenClaw Security Research project:

🔗 [github.com/mbpark/openclaw-research](https://github.com/mbpark/openclaw-research)
