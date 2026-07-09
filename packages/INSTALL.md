# OpenClaw Security Packages Installation Guide

This directory contains production-ready Python packages for OpenClaw security tools.

## Available Packages

1. **vlmguard** - Visual Prompt Injection Defense System
2. **agentic-security** - Agentjacking Defense Framework

## Installation Steps

### Option 1: Install from Source (Recommended)

```bash
# Navigate to packages directory
cd packages

# Install vlmguard
cd vlmguard
pip install -e .
cd ..

# Install agentic-security
cd agentic-security
pip install -e .
cd ..
```

### Option 2: Install Using requirements.txt

```bash
# Install all dependencies
pip install -r requirements.txt

# Install packages in editable mode
cd vlmguard && pip install -e . && cd ..
cd agentic-security && pip install -e . && cd ..
```

### Option 3: Build Distribution Packages

```bash
# Build vlmguard
cd vlmguard
python3 -m pip install build
python3 -m build --outdir dist/
cd ..

# Build agentic-security
cd agentic-security
python3 -m pip install build
python3 -m build --outdir dist/
cd ..

# Install from distribution
pip install dist/vlmguard-0.1.0.tar.gz
pip install dist/agentic-security-0.1.0.tar.gz
```

## Verification

After installation, verify the packages work correctly:

```bash
# Test vlmguard
vlmguard test --verbose

# Test agentic-security
agentic-security test --verbose
```

## Dependencies

### VLMGuard Dependencies

- `torch>=2.0.0` - PyTorch for ML operations
- `transformers>=4.30.0` - Hugging Face transformers
- `sentence-transformers>=2.2.0` - Text embeddings
- `numpy>=1.21.0` - Numerical computing
- `scipy>=1.7.0` - Scientific computing
- `scikit-learn>=1.0.0` - ML utilities
- `pydantic>=2.0.0` - Data validation
- `loguru>=0.6.0` - Logging

### Agentic Security Dependencies

- `pydantic>=2.0.0` - Data validation
- `jsonschema>=4.0.0` - JSON validation
- `loguru>=0.6.0` - Logging
- `pyyaml>=6.0.0` - YAML parsing
- `cryptography>=41.0.0` - Cryptographic operations
- `tokenizers>=0.19.0` - Tokenization

## Troubleshooting

### Issue: pip command not found

Install pip first:

```bash
# For Python 3
python3 -m ensure pip

# Or download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

### Issue: Missing dependencies

Install system dependencies first:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip libssl-dev

# macOS
brew install python

# CentOS/RHEL
sudo yum install python3-devel openssl-devel
```

### Issue: Permission errors

Use virtual environment:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -e vlmguard
pip install -e agentic-security
```

## Quick Reference

### VLMGuard CLI Commands

```bash
# Scan input for malicious content
vlmguard scan "Your input text"

# Analyze intent and detect threats
vlmguard analyze "Your input text"

# Rewrite potentially malicious input
vlmguard rewrite "Your input text"

# Run security tests
vlmguard test --verbose

# Use custom configuration
vlmguard scan "input" --config config.json --threshold 0.7
```

### Agentic Security CLI Commands

```bash
# Validate LLM intent
agentic-security validate '{"action": "read_file", "parameters": {"path": "/app/data.txt"}}'

# Run security tests
agentic-security test --verbose

# Scan environment for threats
agentic-security scan

# Simulate attack scenarios
agentic-security simulate --scenario=workspace_poisoning
```

## Support

For issues or questions:

1. Check the full documentation in `../docs/`
2. Open an issue on GitHub
3. Contact: research@openclaw.ai

## License

Both packages are released under the MIT License.
