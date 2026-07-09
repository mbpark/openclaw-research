# VLMGuard

VLMGuard is a comprehensive defense system against Visual Prompt Injection (VPI) attacks. It provides multiple layers of protection including SVD-based maliciousness estimation, SmoothVLM randomized smoothing, and R1 prompt rewriting.

## Installation

```bash
pip install vlmguard
```

## Quick Start

### Python API

```python
from vlmguard import VLMGuard

# Initialize VLMGuard
vlmguard = VLMGuard()

# Scan input for malicious content
result = vlmguard.scan("Your input text or content")

if result['is_safe']:
    print("Input is safe")
else:
    print(f"Blocked: {result['reason']}")
```

### Command Line

```bash
# Scan input
vlmguard scan "Your input text"

# Analyze intent
vlmguard analyze "Your input text"

# Rewrite potentially malicious input
vlmguard rewrite "Your input text"

# Run security tests
vlmguard test --verbose
```

## Features

- **SVD Maliciousness Scoring**: Uses TF-IDF and Singular Value Decomposition to detect malicious patterns
- **SmoothVLM Protection**: Randomized smoothing to certify robustness against adversarial inputs
- **R1 Prompt Rewriting**: Proactive safety alignment through reasoning-driven rewriting
- **Real-time Scanning**: Fast, efficient threat detection
- **Configurable Thresholds**: Fine-tune sensitivity to your needs

## Configuration

```python
from vlmguard import VLMGuard
import json

config = {
    "svd": {
        "threshold": 0.7,
        "top_k": 50
    },
    "smoothvlm": {
        "num_samples": 10,
        "noise_level": 0.1,
        "certification_threshold": 0.8
    },
    "r1_prompt_rewriter": {
        "enabled": True,
        "reasoning_depth": 3
    }
}

vlmguard = VLMGuard.from_config(config)
```

## Documentation

For detailed architecture, testing procedures, and API reference, see the full documentation:

- [Architecture](../docs/ARCHITECTURE.md)
- [Testing Guide](../docs/TESTING.md)
- [Research Paper](../docs/papers/GatekeeperLLM_Architecture.md)

## License

MIT License - See LICENSE file for details.
