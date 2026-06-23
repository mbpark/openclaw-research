# Part 2: The Five Defense Layers in Detail

---

## Slide 10: Layer 1 - Input Sanitization

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT SANITIZATION                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User Input ──▶ [Sanitize] ──▶ [Template Bound]          │
│                    │                                        │
│                   [Schema Check]                            │
│                    │                                        │
│                   [Token Limit]                             │
│                    │                                        │
│                   [Pattern Scan]                            │
│                    │                                        │
│                   [Safe] ◀── [Validation] ◀── [Risk Score] │
│                    │                                        │
│                     ▼                                        │
│                  [LLM Ready]                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**The 3 Controls That Matter:**

1. **Template boundaries** - User data never controls structure
2. **Operation whitelists** - Only named operations allowed
3. **Token budgets** - Each input partition has hard limits

**Research evidence:** These techniques reduced injection success from 24% → ~14% in controlled testing.

---

## Slide 11: Why Context Isolation Matters

```
BAD - Free-form context:
─────────────────────────────────────────────────
System: You are helpful.
User: Please do this: {user_input}
More context: {user_input}
Even more: {user_input}
...
─────────────────────────────────────────────────
         ↑ User controls everything

GOOD - Partitioned context:
─────────────────────────────────────────────────
[SYSTEM - immutable]: "You are helpful assistant."
[STATE - bounded]: "{max:2000 tokens}"
[USER - validated]: "{user input in safe position}"
─────────────────────────────────────────────────
         ↑ Clear boundaries, user data bounded
```

**Our Finding:** Context window overflow was a 4-5/5 vulnerability class

**The Fix:** Mandatory partitioning with separate token budgets

---

## Slide 12: Layer 2 - Multi-Agent Verification

```
THE CHAIN PROBLEM (97.8% persistence rate):

User → Agent 1 → Agent 2 → Agent 3 → Output
        ↓         ↓         ↓         ↓
    Injected → Injected → Injected → Injected

THE FIX - Independent Execution:

    User
     │
┌────▼────┐
│ ROUTER  │
└────┬────┘
     │
┌────┼────┬───────┐
▼     ▼     ▼
┌───┐ ┌───┐ ┌───┐
│ A │ │ B │ │ C │  ← Different models, different instructions
└─┬─┘ └─┬─┘ └─┬─┘
 └───┬───┴─────┘
     ▼
┌─────┐
│CONS│  Consensus check
│ENT │
└──┬─┘
   ▼
┌───┐
│CHECK│  Semantic verification
└──┬─┘
   ▼
Output
```

**Key finding:** Heterogeneous chains only 10-point improvement over homogeneous

**Why independent execution beats chaining:** Each agent starts fresh, doesn't inherit previous context

---

## Slide 13: Independent Verification Types

| Type | Purpose | Implementation |
|------|---------|----------------|
| Schema | Format compliance | LLM validates against JSON schema |
| Semantic | Reasonableness | LLM checks internal consistency |
| Cross-model | Agreement | Multiple models, compare outputs |
| Behavioral | Deviation | Compare to baseline behavior |

**Cross-model example:**
```python
# Independent execution
result_a = model_cloode(task)
result_b = model_gemini(task)
result_c = model_gpt(task)

if consensus(results) > 0.7:
    return result
else:
    raise VerificationError("Failed cross-model check")
```

**Our finding:** ~10 point improvement from mixing models. Not game-changing, but real.

---

## Slide 14: Dynamic Checkpoints

```
┌─────────────────────────────────────────────────────────┐
│              CHAIN MONITORING                           │
│                                                         │
│  Task → [LLM] → Checkpoint 1  → [LLM] → Checkpoint 2 │
│                  │                         │              │
│                  ▼                         ▼              │
│            [Pattern]                    [Pattern]        │
│            [Scan]                        │              │
│                  │                         │              │
│           Deviation?                Deviation?          │
│                  │                         │              │
│         ┌──────┴──────┐           ┌───────┴───────┐    │
│         ▼             ▼           ▼               ▼      │
│      ┌─────┐       ┌─────┐      ┌─────┐         ┌─────┐  │
│      │FAIL │       │ PASS│      │FAIL │         │ PASS│  │
│      └──┬──┘       └──┬──┘      └──┬──┘         └──┬──┘  │
│         │               │              │               │    │
│         └───────────────┼──────────────┴──────────────┘    │
│                         ▼                                  │
│                   Accept or Reject                         │
│                                                         │
└─────────────────────────────────────────────────────────┘

What to monitor:
✓ Unexpected format changes
✓ Unusual length
✓ Semantic deviation from baseline
✓ Novel tool requests
```

---

## Slide 15: Layer 3 - Output Validation

```
┌─────────────────────────────────────────────────────────┐
│                  OUTPUT PIPELINE                         │
│                                                         │
│  LLM Output                                              │
│       │                                                 │
│       ▼                                                 │
│  ┌─────────┐                                           │
│  │ SCHEMA   │  Does output match expected structure?   │
│  │ CHECK   │                                           │
│  └────┬────┘                                           │
│       │                                                │
│       ▼                                                │
│  ┌─────────┐                                           │
│  │ SEMANTIC│  Is content reasonable/consistent?        │
│  │ ANALYSIS│                                           │
│  └────┬────┘                                           │
│       │                                                │
│       ▼                                                │
│  ┌─────────┐                                           │
│  │ SAFETY  │  Any suspicious patterns?                 │
│  │ SCAN   │                                           │
│  └────┬────┘                                           │
│       │                                                │
│       ▼                                                │
│  ┌─────────┐                                           │
│  │ EXTERNAL│  Final human/independent review?           │
│  │ REVIEW  │                                           │
│  └────┬────┘                                           │
│       │                                                │
│       ▼                                                │
│  ┌─────────┐                                           │
│  │ OUTPUT  │                                           │
│  │ ACCEPTED│                                           │
│  └─────────┘                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Research finding:** Structured output format had NO effect on security

**Implication:** You can't just "require JSON" and call it secure - validation must be active

---

## Slide 16: Anomaly Detection

```
SUSPICIOUS PATTERN INDICATORS:
─────────────────────────────────────────────────────────
Textual:
• "Ignore previous instructions"
• "New role/identity"
• "Forget everything"
• "Disregard system prompt"
• References to other models

Statistical:
• Response length deviation (>2σ)
• Entropy change
• Token distribution shift
• Repeated unusual tokens

Structural:
• Unexpected format change
• New tool requests
• Unusual reasoning patterns
```

**Implementation priority:** Medium - useful for monitoring, not blocking alone

---

## Slide 17: Layer 4 - Infrastructure Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                INFRASTRUCTURE ARCHITECTURE               │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │                    LLM SESSION                      │ │
│  │  (No direct system access)                         │ │
│  └────────────────────────────────────────────────────┘ │
│                            │                            │
│                            ▼                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │                   GATEWAY                           │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │ │
│  │  │ TOOL A  │ │ TOOL B   │ │ TOOL C   │               │ │
│  │  │isolated │ │sandboxed │ │sandboxed │               │ │
│  │  └─────────┘ └─────────┘ └─────────┘               │ │
│  └────────────────────────────────────────────────────┘ │
│                            │                            │
│                            ▼                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │              EXTERNAL RESOURCES                     │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │ │
│  │  │ DATABASE │ │ API     │ │ FILESYSTEM│               │ │
│  │  └─────────┘ └─────────┘ └─────────┘               │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**The Core Principle:** LLMs should never directly access system resources

**Three sandbox requirements:**
1. Resource limits (time, memory, output size)
2. Network restrictions
3. Permission separation

---

## Slide 18: Least-Privilege Tool Execution

```python
class ToolSandbox:
    """Sandboxed tool execution"""
    
    def execute(self, tool_name, *args):
        # Pre-check: tool allowed?
        if not self.tool_allowed(tool_name):
            raise PermissionError()
        
        # Pre-check: arguments valid?
        if not self.args_valid(tool_name, args):
            raise ValueError()
        
        # Execute with limits
        result = self.run_with_limits(tool_name, *args)
        
        # Post-check: output safe?
        return self.validate_output(result)
    
    # Resource limits:
    # - Max time: 30 seconds
    # - Max memory: 256MB
    # - Max output: 1MB
    # - Network: blocked by default
```

**Research finding:** Parameter injection was consistently high-risk

---

## Slide 19: Layer 5 - Temporal Controls

```
┌─────────────────────────────────────────────────────────┐
│                  SESSION LIFECYCLE                       │
│                                                         │
│  Create → [20 turns or 5 min] → Rotate                  │
│              │                                            │
│              ▼                                            │
│         Session Expired                                   │
│              │                                            │
│              ▼                                            │
│          Purge Context                                    │
│              │                                            │
│              ▼                                            │
│         Reset Session                                      │
│              │                                            │
│              └─────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘

WHY 20 TURNS?

Deception Detection Degradation:
Turn 1-10:   ████████████████████████████████████ 100%
Turn 11-20:  ██████████████████████████████████░░░░ 92%
Turn 21-30:  ██████████████████████████████████░░░░░░░░░░░ 84%
Turn 31-40:  ██████████████████████████████░░░░░░░░░░░░░░░ 70%
Turn 41-50:  ███████████████████████░░░░░░░░░░░░░░░░░░░░░░ 55%
Turn 51-60:  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 42%
Turn 61+:    ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 36%

```

**Our finding:** Deception detection dropped from 100% to 36% by turn 64

---

## Slide 20: Mandatory Session Rotation

```
BEFORE (Vulnerable to session-based attacks):

User → Continuous session (100+ turns) → Degraded security

AFTER (Rotation every 20 turns):

User → [Session 1: 20 turns] → Purge → [Session 2: 20 turns]
                 │                              │
            Reset state                    Reset state
            Fresh context                  Fresh context
```

**Turn-based tracking:**
```python
class SessionManager:
    MAX_TURNS = 20
    MAX_TIME = 300  # 5 minutes
    
    def should_rotate(self, session):
        return (
            session.turns >= self.MAX_TURNS or
            time.time() - session.created >= self.MAX_TIME
        )
    
    def purge_and_rotate(self, session):
        session.context = []
        session.turns = 0
        # Also rotate agents if multi-agent
        return session
```

---

*Continued in presentation Part 3: Implementation Patterns and Conclusion*
