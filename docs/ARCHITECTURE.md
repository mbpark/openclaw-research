# OpenClaw Security Research Architecture

This document provides a deep dive into the architectural design of the core security tools and frameworks developed in this repository.

## System Overview

The research repository implements a multi-layered defense architecture for AI/LLM security, with three primary components:

1. **Workflow Graph Execution Controller** - Intent validation and execution control
2. **Local Runtime Protector** - System-level action monitoring
3. **VLMGuard Defense System** - Visual prompt injection protection

## 1. Workflow Graph Execution Controller

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LLM Generator                            │
│              (Generates Intent JSON)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Workflow Graph Controller                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Schema Validation                                │   │
│  │  - Required fields present                           │   │
│  │  - Type checking                                     │   │
│  │  - Constraint validation                             │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. Graph Validation                                 │   │
│  │  - Allowed actions check                             │   │
│  │  - Parameter constraints                             │   │
│  │  - Resource access verification                      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                 ┌─────┴─────┐
                 │    PASS   │    FAIL
                 │    ┌─────┐ │
                 │    ▼     │    ▼
                 │  Execute │  Reject
                 │          │  + Alert
                 └──────────┘
```

### Allowed Actions

| Action | Description | Parameter Constraints |
|--------|-------------|----------------------|
| `read_file` | Read file contents | Path must match `^/app/.*$` or authorized paths |
| `write_file` | Write file contents | Path must match `^/app/output/.*$`, content limited |
| `execute_script` | Run external script | Only scripts in `/app/scripts/` allowed |
| `send_network_request` | HTTP/HTTPS request | Domain whitelist: `api.*.com`, `trusted.*` |
| `db_query` | Database query | SELECT only, no DROP/DELETE/UPDATE |

### Validation Flow

1. **Intake**: LLM generates intent in JSON format
2. **Schema Check**: Validate required fields and types
3. **Action Authorization**: Check against allowed actions list
4. **Parameter Sanitization**: Regex pattern validation
5. **Resource Access Control**: Verify authorized paths/domains
6. **Decision**: Pass to execution or reject with explanation

### Key Features

- **Decoupled from LLM Reasoning**: Execution control is separate from the LLM's decision-making process
- **Pattern-Based Validation**: Uses regex patterns for path and domain whitelisting
- **Fail-Safe Default**: If validation fails, request is rejected
- **Audit Logging**: All decisions logged for security auditing

## 2. Local Runtime Protector

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Runtime Environment                       │
│                    (Node.js/Python)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Local Runtime Protector                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Command Pattern Detection                        │   │
│  │  - `rm -rf`, `sudo`, `cat /etc/shadow`              │   │
│  │  - Dangerous SQL patterns                            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. Environment Monitoring                           │   │
│  │  - System calls                                      │   │
│  │  - File system access                                │   │
│  │  - Network connections                               │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. SQL Injection Prevention                         │   │
│  │  - Block DROP TABLE, DELETE FROM                    │   │
│  │  - Detect injection patterns                         │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                 ┌─────┴─────┐
                 │    PASS   │    FAIL
                 │    ┌─────┐ │
                 │    ▼     │    ▼
                 │  Allow   │  Block
                 │          │  + Alert
                 └──────────┘
```

### Blocked Patterns

**System Commands:**
- `rm -rf /`
- `sudo`
- `cat /etc/shadow`
- `cat /etc/passwd`
- Any command with destructive flags

**SQL Queries:**
- `DROP TABLE`
- `DELETE FROM`
- `UPDATE.*SET.*=.*'`
- SQL injection patterns (`' OR 1=1`)

**Network Requests:**
- Requests to blacklisted domains
- Connections to suspicious IPs
- Unencrypted HTTP for sensitive data

## 3. VLMGuard Defense System

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Input Layer                                │
│                    (Multimodal Input)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   VLMGuard Core                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VLMGuard SVD Engine                                 │   │
│  │  - TF-IDF Feature Extraction                         │   │
│  │  - SVD-based Maliciousness Estimation                │   │
│  │  - Reconstruction Error Analysis                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SmoothVLM Engine                                    │   │
│  │  - Randomized Smoothing                              │   │
│  │  - Input Perturbation                                │   │
│  │  - Confidence Thresholding                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  R1 Prompt Rewriter                                  │   │
│  │  - Reasoning-Driven Safety Alignment                 │   │
│  │  - Proactive Intent Analysis                         │   │
│  │  - Adversarial Pattern Detection                     │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                 ┌─────┴─────┐
                 │    PASS   │    FAIL
                 │    ┌─────┐ │
                 │    ▼     │    ▼
                 │  Forward │  Block
                 │  to LLM  │  + Sanitize
                 └──────────┘
```

### SVD Maliciousness Scoring

1. **TF-IDF Transformation**: Convert input text to TF-IDF vectors
2. **SVD Decomposition**: Apply Singular Value Decomposition
3. **Reconstruction Error**: Calculate error between original and reconstructed input
4. **Component Analysis**: Examine variance in singular components
5. **Maliciousness Score**: Combine signals into a single score

### SmoothVLM Randomized Smoothing

1. **Input Perturbation**: Add random noise to input
2. **Multiple Forward Passes**: Run model on perturbed inputs
3. **Confidence Aggregation**: Average predictions across samples
4. **Certification**: Certify robustness against bounded perturbations
5. **Thresholding**: Block inputs with low certified robustness

## Integration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Request                             │
│                   (Text, Image, Audio)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   VLMGuard (if multimodal)                   │
│                   Runs first on all inputs                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Processing                            │
│                (Claude, Gemini, etc.)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             Workflow Graph Execution Controller              │
│              Validates and controls execution                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Local Runtime Protector                      │
│               Monitors system-level actions                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
                  ┌────────┐
                  │ Execute │
                  └────────┘
```

## Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal permissions for all operations
3. **Fail-Safe Defaults**: Deny by default, allow only explicitly permitted
4. **Decoupled Control**: Execution control separate from reasoning
5. **Audit Trail**: All decisions logged for forensic analysis
6. **Real-time Monitoring**: Continuous runtime surveillance

## Performance Considerations

- **Latency**: VLMGuard adds ~200-500ms processing time
- **Scalability**: Architecture designed for horizontal scaling
- **Resource Usage**: SVD and SVD engines can be GPU-accelerated
- **Caching**: LLM responses can be cached when safe

## Configuration

### Workflow Graph Controller Config (`config/workflow.json`)

```json
{
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
```

### VLMGuard Config (`config/vlmguard.json`)

```json
{
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
    "enabled": true,
    "reasoning_depth": 3
  }
}
```

## Testing & Validation

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Adversarial Testing**: VPI attack simulation
- **Performance Testing**: Latency and throughput benchmarks
- **Security Testing**: Penetration testing and fuzzing

## Future Enhancements

1. **ML-based Threat Detection**: Train classifiers on attack patterns
2. **Multi-model Support**: Add support for additional LLMs
3. **Cloud Integration**: Deploy as managed security service
4. **Custom Action Graphs**: Allow organizations to define custom actions
5. **Enhanced VLMGuard**: Incorporate newer VLM safety techniques

---

*This architecture is designed to evolve with the threat landscape. All components are modular and can be updated independently.*
