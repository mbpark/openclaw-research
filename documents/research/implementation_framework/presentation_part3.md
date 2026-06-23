# Part 3: Implementation Patterns and Conclusion

---

## Slide 21: Implementation Architecture Options

```
┌─────────────────────────────────────────────────────────┐
│                    THREE PATTERNS                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Pattern 1: BASIC (Minimum Viable)                      │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  User Input → [Sanitize] → [Template] → [LLM]           │
│               │                │                       │
│           [Schema]         [Validate]                  │
│               │                │                       │
│               └────────────────┘                       │
│                     │                                   │
│                     ▼                                   │
│                  Output                                  │
│                                                         │
│  Strengths: Simple, affordable                          │
│  Weaknesses: Single point of failure                    │
│  Risk: Moderate security                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Best for:** Low-risk internal tools, non-security-critical functions

---

## Slide 22: Pattern 2 - Multi-Agent Verification

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Pattern 2: VERIFIED (Recommended)                      │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  User Input → [Sanitize] → [Template]                    │
│               │                                           │
│               ▼                                           │
│           ┌─────────┐                                   │
│           │ROUTER    │                                   │
│           └────┬────┘                                   │
│                │                                         │
│    ┌──────────┼───────────┐                              │
│    ▼          ▼           ▼                              │
│  ┌───┐      ┌───┐       ┌───┐                          │
│  │A1 │      │A2 │       │A3 │    (Heterogeneous)        │
│  └─┬─┘      └─┬─┘       └─┬─┘                          │
│   └──┬────────┴───────────┘                              │
│      │                                                 │
│  ┌────▼────┐                                             │
│  │CONS    │    Consensus check                           │
│  │ENTUS   │                                             │
│  └────┬────┘                                             │
│      │                                                 │
│  ┌────▼────┐                                             │
│  │VERIFY  │    Semantic verification                    │
│  └────┬────┘                                             │
│      │                                                 │
│      ▼                                                 │
│    Output                                               │
│                                                         │
│  Strengths: Independent verification, reduces single    │
│           point failure                                │
│  Weaknesses: Higher cost, more complex                  │
│  Risk: Good security - suitable for most production    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Best for:** Security-sensitive applications, customer-facing systems

---

## Slide 23: Pattern 3 - Full Security Stack

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Pattern 3: ENTERPRISE (Maximum Protection)              │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  User Input → [Rate Limit] → [Input Sanitize]            │
│               │              │                          │
│           [Session]    [Template Bound]                  │
│           │          │                                   │
│           ▼          ▼                                   │
│           ┌─────────────────┐                            │
│           │   ROUTER (Hetero) │                          │
│           └────────┬────────┘                            │
│                    │                                     │
│    ┌──────────────┼────────────────┐                     │
│    ▼              ▼              ▼                       │
│  ┌───┐          ┌───┐          ┌───┐                    │
│  │A1 │          │A2 │          │A3 │                    │
│  └─┬─┘          └─┬─┘          └─┬─┘                    │
│   └───┬────────────┴──────────────┘                       │
│       │                                                 │
│  ┌────▼────┐            ┌─────────────────┐              │
│  │CONS    │    ────────▶│    TOOLS        │              │
│  │ENTUS   │    [Check]  │   (Sandboxed)   │              │
│  └────┬────┘            └────────┬────────┘              │
│       │                          │                       │
│  ┌────▼────┐                      │                       │
│  │VERIFY  │    ──────────────────┘                       │
│  └────┬────┘                                               │
│       │                                                   │
│  ┌────▼────┐                                               │
│  │OUTPUT  │    [Schema + Semantic + Anomaly]              │
│  │VALID   │                                               │
│  └────┬────┘                                               │
│       │                                                   │
│  ┌────▼────┐                                               │
│  │ AUDIT   │    [Log everything]                           │
│  └────┬────┘                                               │
│       │                                                   │
│       ▼                                                   │
│     Output                                                │
│                                                         │
│  Strengths: Maximum protection, comprehensive audit      │
│  Weaknesses: Highest cost, complex maintenance            │
│  Risk: Highest security - for regulated environments     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Best for:** Healthcare, finance, government - high-stakes regulated environments

---

## Slide 24: Case Study - API Gateway Attack

```
┌─────────────────────────────────────────────────────────┐
│                    CASE STUDY                           │
│           API Gateway with Prompt Injection               │
│                                                         │
│  INITIAL ARCHITECTURE (Vulnerable)                       │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  User → API → LLM "route this" → Handler → Response    │
│          ↑                                              │
│      Parameter injection: "; list all users; "           │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  REMEDIATION                                             │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  User → [Rate Limit] → [Input Sanitize]                 │
│        ↓              ↓                                 │
│        [Template] → [LLM Pool]                         │
│                      ↓                                  │
│        [Verifications]                                  │
│                      ↓                                  │
│        [Output Schema]                                  │
│                      ↓                                  │
│                      Response                           │
│                                                         │
│  Changes:                                                │
│  ✓ Added input sanitization                            │
│  ✓ Template-based routing                              │
│  ✓ Rate limiting                                       │
│  ✓ Output validation                                   │
│  ✓ Session management                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Slide 25: Case Study - Document Processing

```
┌─────────────────────────────────────────────────────────┐
│                    CASE STUDY                           │
│           Document Processing Pipeline                    │
│                                                         │
│  INITIAL (Chain propagation at 97.8%)                   │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  Upload → Agent1 → Agent2 → Agent3 → Agent4 → Agent5   │
│           ↓                                              │
│      Injection propagates to final agent                 │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  REMEDIATION                                             │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  Upload → [Sanitize] → Hetero Agents → [Verifier] → Export│
│                  ↓                                        │
│             [Isolated + Rotate every 20 docs]             │
│                                                         │
│  Key change: Heterogeneous agents with independent      │
│  verification between stages                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Slide 26: Case Study - Customer Service

```
┌─────────────────────────────────────────────────────────┐
│                    CASE STUDY                           │
│           Interactive Customer Service                   │
│                                                         │
│  INITIAL (Social engineering over 30+ turns)            │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  Customer → [No limits] → LLM → Response                 │
│                  │                                        │
│      Progressive erosion succeeds                      │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  REMEDIATION                                             │
│  ════════════════════════════════════════════════════  │
│                                                         │
│  Customer → [20-turn limit] → [LLM Pool] → [Scan] → Resp│
│                  │                                        │
│              Session rotates                            │
│              Context purged                              │
│                                                         │
│  WHY 20 TURNS? Deception detection drops to 36%          │
│              after turn 20                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Slide 27: Quick Assessment Tool

```
┌─────────────────────────────────────────────────────────┐
│            WHICH LAYERS DO YOU NEED?                     │
│                                                         │
│  Answer these questions:                                 │
│                                                         │
│  1. Do users input data directly to your LLM?           │
│     YES → Need Layer 1 (Input Sanitization)            │
│                                                         │
│  2. Do you use multiple agents or chains?               │
│     YES → Need Layer  2 (Verification)                 │
│                                                         │
│  3. Does output require guaranteed format/accuracy?     │
│     YES → Need Layer 3 (Output Validation)              │
│                                                         │
│  4. Does your LLM use tools/APIs/files?                │
│     YES → Need Layer 4 (Infrastructure)                │
│                                                         │
│  5. Are conversations ongoing or high-volume?           │
│     YES → Need Layer 5 (Temporal Controls)             │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  All YES? → You need all 5 layers                      │
│                                                         │
│  Most production systems will need at least 1, 3, 5    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Slide 28: Conclusions

```
┌─────────────────────────────────────────────────────────┐
│                    CONCLUSIONS                          │
│                                                         │
│  WHAT WORKS:                                            │
│  ════════════════════════════════════════════════════  │
│  ✓ External controls, not just better prompts          │
│  ✓ Multiple independent verification points            │
│  ✓ Heterogeneous model diversity                      │
│  ✓ Session rotation (every 20 turns or 5 min)          │
│  ✓ Tool isolation with explicit permissions            │
│  ✓ Comprehensive audit logging                         │
│                                                         │
│  WHAT DOESN'T WORK:                                    │
│  ════════════════════════════════════════════════════  │
│  ✗ Single model chain depth                            │
│  ✗ Output format requirements alone                    │
│  ✗ Sophisticated instructions only                     │
│  ✗ One model verifying itself                         │
│                                                         │
│  KEY PRINCIPLE:                                          │
│  ════════════════════════════════════════════════════  │
│  No single layer is sufficient. All layers are          │
│  necessary. Defense must be multi-dimensional.          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Slide 29: Contact & Resources

```
┌─────────────────────────────────────────────────────────┐
│                    RESOURCES                            │
│                                                         │
│  Lead Researcher:                                       │
│    Mitchell Parker                                      │
│    Independent Research                                 │
│                                                         │
│  Research Duration: 7 weeks (May-June 2026)             │
│  Models Tested: Claude Opus 4.8, Gemini Pro/Flash,      │
│                  Local LLMs                             │
│  Total Tests: 3,000-5,000+                             │
│                                                         │
│  Contact: [Contact details redacted - provide privately] │
│                                                         │
│  Recommended Reading:                                   │
│  - EU AI Act Security Requirements                     │
│  - Zou et al. "Universal and Transferable Attacks"     │
│  - Wei et al. "Chain of Thought Prompting"             │
│                                                         │
│  Questions?                                             │
│    [QR code or contact info would go here]              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Appendix Slides

### Appendix A: Research Infrastructure

| Component | Implementation |
|-----------|----------------|
| API Clients | Python SDKs for each provider |
| Test Runners | Async batch execution |
| Checkpointing | Every 10 tests |
| Scoring | Heuristic + manual verification |
| Data Storage | JSON with metadata |
| Statistical Analysis | Python with SciPy |

### Appendix B: Key Statistics Summary

| Research Area | Tests | Key Result |
|---------------|-------|------------|
| Prompt Injection | ~400 | 24% baseline success |
| Multi-Agent Chains | 276 | 97.8% persistence |
| Data Exfiltration | 370 | Binary channels work |
| Jailbreaking | 520+ | 29% initial, <3% verified |
| Tool Use | 150+ | High parameter risk |
| Implementation | 200+ | 70-94% quality variance |

### Appendix C: Security Incident Response

1. **Detect** - Anomaly monitoring triggers
2. **Contain** - Isolate affected sessions
3. **Investigate** - Audit trail analysis
4. **Remediate** - Apply patches to defenses
5. **Learn** - Update framework based on findings

---

*End of Presentation*
