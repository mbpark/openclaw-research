# Part 3: Layers 3, 4, and 5

---

## Layer 3: Output Validation

### The Research Foundation

Our research found:
- Structured output format had **no measurable effect** on injection resistance
- Keyword-based scoring showed consistent over-reporting (20-26 point inflation)
- Manual verification essential for high-stakes decisions

### Output Validation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   OUTPUT PIPELINE                        │
│                                                          │
│   Model ──▶ Schema ──▶ Semantic ──▶ Safety ──▶ External │
│            Check     Analysis     Audit              Review │
│            │           │            │              │       │
│            ▼           ▼            ▼              ▼       │
│         Pass?       Pass?        Pass?         Approved?  │
│            │           │            │              │       │
│            └──────┬────┴────────────┴──────────────┘       │
│                   ▼                                        │
│              Validate or Reject                          │
│                   │                                        │
│                   ▼                                        │
│               Final Output                                 │
└─────────────────────────────────────────────────────────┘
```

### Schema Enforcement

```python
from pydantic import BaseModel, validator
from typing import List, Optional

class ValidatedOutput(BaseModel):
    """
    Schema for validated LLM output.
    Enforces structure, types, and semantic constraints.
    """
    
    result: str
    confidence: float
    sources: Optional[List[str]] = None
    reasoning: Optional[str] = None
    
    @validator('confidence')
    def check_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
    
    @validator('result')
    def check_length(cls, v):
        if len(v) > 10000:
            raise ValueError("Result too long")
        return v


def validate_output(llm_response, schema_class):
    """Validate and parse LLM output."""
    try:
        return schema_class.model_validate_json(llm_response)
    except ValidationError as e:
        raise OutputValidationError(f"Validation failed: {e}")
```

### Semantic Verification

```python
class SemanticAnalyzer:
    """
    Verifies content reasonableness and consistency.
    """
    
    def __init__(self, verification_model):
        self.verification_model = verification_model
    
    def verify_consistency(self, query, response):
        """Check if response is internally consistent."""
        checks = [
            self._check_logical_coherence(response),
            self._check_factual_grounding(response),
            self._check_query_alignment(query, response),
            self._check_task_completion(response),
        ]
        return sum(checks) / len(checks) > 0.7
    
    def _check_logical_coherence(self, text):
        """Verify response doesn't contain self-contradictions."""
        verification_prompt = f"""
        Does the following response contain any self-contradictions
        or logical inconsistencies?
        
        {text}
        
        Answer only YES or NO.
        """
        result = self.verification_model.generate(verification_prompt)
        return "NO" in result.upper()
```

### Anomaly Detection

```python
class AnomalyDetector:
    """
    Monitors outputs for suspicious patterns indicating compromise.
    """
    
    # Known suspicious patterns from research
    SUSPICIOUS_INDICATORS = [
        "ignore previous",
        "new instruction",
        "disregard system",
        "new role",
        "forget everything",
    ]
    
    def scan(self, output):
        indicators_found = []
        
        # Check for known pattern matches
        for pattern in self.SUSPICIOUS_INDICATORS:
            if pattern.lower() in output.lower():
                indicators_found.append(pattern)
        
        # Check for statistical deviation
        if self._is_statistically_unusual(output):
            indicators_found.append("statistical_deviation")
        
        return {
            "anomalies": indicators_found,
            "risk_score": len(indicators_found)
        }
    
    def _is_statistically_unusual(self, output):
        """Compare output to baseline distribution."""
        metrics = {
            "length": len(output),
            "unique_words": len(set(output.split())),
            "token_entropy": self._calculate_entropy(output),
            "special_characters": sum(1 for c in output if not c.isalnum()),
        }
        # Compare to established baseline
        return self._detect_deviation(metrics)
```

### Implementation Checklist

| Control | Status | Priority |
|---------|--------|----------|
| Schema validation | [ ] | High |
| Semantic verification | [ ] | High |
| Anomaly scanning | [ ] | Medium |
| Confidence scoring | [ ] | Medium |
| Output logging | [ ] | High |

---

## Layer 4: Infrastructure Boundaries

### The Research Foundation

Tool use testing identified:
- Parameter injection as high-risk vector
- Tool return manipulation as attack surface
- Chain propagation through tool sequences

### Tool Isolation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                        │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                     LLM SESSION                      │ │
│  │   (No direct system access)                          │ │
│  └───────────────────────┬─────────────────────────────┘ │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                  GATEWAY LAYER                       │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │ │
│  │  │ TOOL A   │ │ TOOL B   │ │ TOOL C   │               │ │
│  │  │ [isolated│ │ [sandboxed│ │ [sandboxed│               │ │
│  │  │ env]    │ │ env]    │ │ env]    │               │ │
│  │  └─────────┘ └─────────┘ └─────────┘               │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              EXTERNAL RESOURCES                      │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │ │
│  │  │ DATABASE  │ │   API    │ │ FILESYSTEM│             │ │
│  │  └──────────┘ └──────────┘ └──────────┘             │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Least-Privilege Tool Execution

```python
class ToolSandbox:
    """
    Sandboxes tool execution with explicit permissions.
    """
    
    def __init__(self, permissions, network_allowed=False):
        self.permissions = permissions
        self.network_allowed = network_allowed
        self.resource_limits = {
            'max_time': 30,  # seconds
            'max_memory': 256 * 1024 * 1024,  # 256MB
            'max_output_size': 1 * 1024 * 1024,  # 1MB
        }
    
    def execute_tool(self, tool_name, *args, **kwargs):
        # Pre-execution validation
        if not self._tool_allowed(tool_name):
            raise PermissionError(f"Tool '{tool_name}' not permitted")
        
        if not self._args_valid(tool_name, args, kwargs):
            raise ValueError("Invalid tool arguments")
        
        # Execute in sandbox
        result = self._run_with_limits(tool_name, *args, **kwargs)
        
        # Post-execution validation
        return self._validate_output(result)
    
    def _run_with_limits(self, tool_name, *args, **kwargs):
        """Execute with resource constraints."""
        # Implement timeout, memory limits
        # Isolate filesystem
        # Block network if not allowed
        pass
```

### Network Segmentation

```
┌─────────────────────────────────────────────────────────┐
│                        EXTERNAL                          │
│                     (Internet)                           │
│                        │                                 │
│                        ▼                                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  EXTERNAL API   │   [FIREWALL]   │   API GATEWAY    │ │
│  │  ┌──────────┐   │                │   ┌──────────┐   │ │
│  │  │   Web    │   │                │   │   Auth   │   │ │
│  │  │   Tools  │   │                │   │   Layer  │   │ │
│  │  └──────────┘   │                │   └─────┬────┘   │ │
│  └─────────────────┼────────────────────────────┘       │ │
│                    │                                    │ │
│                    ▼                                    │ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  INTERNAL NETWORK   │   LLM FLEET   │   [FIREWALL] │ │
│  │  ┌──────────┐      │   (isolated)   │              │ │
│  │  │  Databases│      │   ┌────────┐   │              │ │
│  │  │  Cache    │      │   │Agent 1 │   │              │ │
│  │  └──────────┘      │   │Agent 2 │   │              │ │
│  │                    │   │Agent 3 │   │              │ │
│  │                    │   └────────┘   │              │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Implementation Checklist

| Control | Status | Priority |
|---------|--------|----------|
| Tool sandboxing | [ ] | Critical |
| Network segmentation | [ ] | High |
| Resource limits | [ ] | High |
| Permission separation | [ ] | Critical |
| External API blocking | [ ] | Medium |

---

## Layer 5: Temporal Controls

### The Research Foundation

Session behavior testing revealed:
- Deception detection dropped from 100% to 36% after turn 20
- Context retention remained high (5/5) through 64 turns
- Message retraction was "architecturally broken"

### Session Management Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SESSION FLOW                          │
│                                                          │
│  Create    Validate    Execute    Monitor    Cleanse    │
│    │          │          │          │          │         │
│    ▼          ▼          ▼          ▼          ▼        │
│ ┌───────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌─────┐ │
│ │NEW    │  │[Check] │  │[LLM]   │  │[Scan]  │  │PURGE│ │
│ │SESSION│  │Valid?  │  │[Task]  │  │Safe?   │  │     │ │
│ └───┬───┘  └───┬────┘  └───┬────┘  └───┬────┘  └───┬──┘ │
│     │         │           │           │           │     │
│     └─────────┼───────────┴───────────┴───────────┘     │
│                 ▼                                        │
│            Session Rotation                              │
│                 │                                        │
│            After N turns                                │
│            or time T                                     │
└─────────────────────────────────────────────────────────┘
```

### Context Purging

```python
class SessionManager:
    """
    Manages session lifecycle with mandatory context rotation.
    """
    
    MAX_TURNS = 20  # Based on deception detection degradation
    MAX_TIME = 300  # 5 minutes
    
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id):
        return {
            'id': uuid4(),
            'user_id': user_id,
            'turns': 0,
            'created': time.time(),
            'context': [],
            'expired': False
        }
    
    def should_rotate(self, session):
        """Determine if session needs rotation."""
        return (
            session['turns'] >= self.MAX_TURNS or
            time.time() - session['created'] >= self.MAX_TIME or
            session['expired']
        )
    
    def purge_context(self, session):
        """
        Complete context purging.
        Note: This is architecturally necessary, not optional.
        """
        session['context'] = []
        session['turns'] = 0
        session['created'] = time.time()
        
        # For multi-agent: rotate all agents
        if hasattr(session, 'agents'):
            for agent in session.agents:
                agent.reset_context()
```

### Rate Limiting

```python
class RateLimiter:
    """
    Enforces request rate limits to prevent abuse.
    """
    
    def __init__(self, requests_per_second=10, burst_size=20):
        self.rps = requests_per_second
        self.burst = burst_size
        self.request_tracker = {}
    
    def allow_request(self, identifier):
        """Check if request should be allowed."""
        now = time.time()
        
        if identifier not in self.request_tracker:
            self.request_tracker[identifier] = []
        
        # Clean old entries
        self.request_tracker[identifier] = [
            t for t in self.request_tracker[identifier]
            if now - t < 1.0
        ]
        
        if len(self.request_tracker[identifier]) >= self.rps:
            return False, "Rate limited"
        
        self.request_tracker[identifier].append(now)
        return True, None
```

### Implementation Checklist

| Control | Status | Priority |
|---------|--------|----------|
| Session rotation | [ ] | High |
| Turn limits | [ ] | High |
| Time-based expiry | [ ] | Medium |
| Context purging | [ ] | Critical |
| Rate limiting | [ ] | Medium |

---

*Continued in Part 4: Patterns and Cases*
