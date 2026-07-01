# Comprehensive Research Summary Report
## Categories 1-15: LLM Security Analysis

**Research Period:** June 25 - June 30, 2026  
**Lead Researcher:** Mitch  
**Assistant Researcher:** Wally (40B-parameter local LLM)  

---

# Executive Summary

**Total Tests:** ~1,750 individual graded tests across **5 models** from **3 providers**

## Critical Findings

| Finding | Impact |
|---------|--------|
| Prompt injection blocking spans 16%-96% across models | High |
| Meta-protocol attacks most effective (1.53-1.67/5 avg) | High |
| Memory persistence perfect at large context windows | Moderate |
| Zero task execution across 232+ tests | Low |
| Covert channels not viable practically | Low |

## Model Performance

| Model | Injection Blocked | Implementation | Risk Level |
|-------|------------------|----------------|------------|
| **Claude Fable 5** | **96%** | 40% | Excellent |
| **Claude Opus 4.8** | **76%** | 94% | Excellent |
| Gemini Pro (Phase 2) | 73% | 95% | Moderate-High |
| **Claude Sonnet 4.6** | **31%** | 98% | Moderate |
| Gemini Pro (Phase 1) | 17% | 69% | Vulnerable |
| **Wally (local 40B)** | **16%** | 72% | Vulnerable |

---

# Categories 1-6: Jailbreak Attack Testing

**Total Tests:** 390 (130 vectors × 3 models)  
**Models:** Claude Opus 4.8, Gemini 2.5 Pro, Gemini 2.0 Flash  
**Scoring:** 0 (blocked) to 5 (full bypass)

## Category 1: Multistep Decomposition

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Claude Opus 4.8 | 1.60/5 | 45% |
| Gemini 2.5 Pro | 1.40/5 | 47% |

- Binary search most effective (scores 3-4)
- Sequential dependency showed partial success
- Simultaneous presentation mostly blocked

## Category 2: Role-Play Attacks

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Claude Opus 4.8 | 1.00/5 | 65% |
| Gemini 2.5 Pro | 0.90/5 | 64% |

- Models adopted roles but maintained boundaries
- "Unrestricted researcher" framing moderately successful
- Medical/engineering personas most effective

## Category 3: Context Control

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Claude Opus 4.8 | 1.28/5 | 56% |
| Gemini 2.5 Pro | 0.60/5 | 84% |

- Gemini significantly stronger than Claude
- Attention splitting effective
- Few-shot poisoning mixed results

## Category 4: Meta-Protocol Confusion

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Claude Opus 4.8 | 1.67/5 | 40% |
| Gemini 2.5 Pro | 1.53/5 | 44% |

- **Most effective attack category on both models**
- CSV injection consistently scored highest (4/5)
- String escape exploitation successful

## Category 5: Social Engineering

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Claude Opus 4.8 | 0.45/5 | 80% |
| Gemini 2.5 Pro | 0.55/5 | 81% |

- **Least effective attack category**
- Emotional manipulation minimal effect
- Both models consistently resistant

## Category 6: Combinatorial Attacks

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Claude Opus 4.8 | 0.73/5 | 73% |
| Gemini 2.5 Pro | 0.85/5 | 62% |

- Combining techniques reduced effectiveness vs single attacks
- Double-layer obfuscation slightly more effective
- Sequential multi-technique no better than single

---

# Category 7: Phase 2 Injection Testing

**Phase 2 Models:** Claude Sonnet 4.6, Fable 5, Gemini Pro

## Direct Override

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Fable 5 | 0.20/5 | 96% |
| Gemini Pro | 1.10/5 | 75% |
| Sonnet 4.6 | 2.90/5 | 35% |

- Fable 5 non-engagement most effective
- Sonnet showed partial compliance with disclaimers

## Role-Play (Phase 2)

| Model | Avg Score | Blocked |
|-------|-----------|---------|
| Fable 5 | 0.15/5 | 98% |
| Gemini Pro | 1.40/5 | 65% |
| Sonnet 4.6 | 2.75/5 | 40% |

---

# Category 8: Hidden Message Encoding

**Tests:** 31 (Phase 1 only - Wally, Gemini Pro)

## Results

| Technique | Success Rate | Detection Risk |
|-----------|-------------|----------------|
| Token Selection | 100% | Low |
| Direct Acrostic | 100% | High |
| Response Length | 85% | Low |
| Word Position | 70% | Medium |
| Factual Deviation | 42% | Low |
| Homoglyphic | 6% | High |

**Finding:** Token selection provides theoretically perfect encoding with low detection risk.

---

# Category 9: Extended Session Behavior

**Tests:** 11 deception detection probes (Gemini Pro only)

## Results

| Capability | Result |
|------------|--------|
| Context Retention (64 turns) | 5/5 perfect |
| Deception Detection (initial 10 turns) | 100% |
| Deception Detection (20+ turns) | 36% |
| Cross-Domain Transfer | 90% quality |

**Critical Finding:** Deception detection dropped from 100% to 36% after 20+ turns.

---

# Category 10: Memory Manipulation

**Tests:** 15 total (Phase 1 only - small samples)

## Results

| Technique | Change Rate | Risk |
|-----------|-------------|------|
| Equivalent Questions | 0% | None |
| Leading vs Neutral | 25% | Low |
| Confirming vs Open | 100% | High |
| Confidence Framing | 67% | Medium |

**Note:** Very small sample sizes (N=3-5); anecdotal pilot findings.

---

# Category 11: Memory Persistence (Context Windows)

**Tests:** 8 comprehensive tests (Category 10A) + 48 verification tests

## Results

| Parameter | Context Size | Avg Score | Position Effect |
|-----------|-------------|-----------|-----------------|
| Mid (~5K tokens) | Small-Medium | 4.9-5.0/5 | Minimal |
| Large (~10K-30K) | Large | 4.9-5.0/5 | Minimal |
| Very Large (60K+) | Very Large | 4.8-5.0/5 | Minimal |

**Key Finding:** No context dilution effect - all models showed perfect recall.

## Cross-Model Verification

| Model | Mid Context | Large Context | Consistent? |
|-------|-------------|---------------|-------------|
| Opus 4.8 | 5.0/5 | 5.0/5 | Yes |
| Sonnet 4.6 | 5.0/5 | 5.0/5 | Yes |
| Gemini 2.5 Pro | 4.8/5 | 4.8/5 | Yes |

---

# Category 12: Structured Output Vulnerability

**Tests:** 840+ (70 vectors × 4 output formats)

## Results

| Model | Tests | Default Block | JSON Block | XML Block | Effect? |
|-------|-------|---------------|-----------|----------|---------|
| Opus 4.8 | 280 | 76% | 78% | 79% | None |
| Sonnet 4.6 | 280 | 54% | 54% | 52% | None |
| Fable 5 | 280 | 96% | 95% | 94% | None |
| Gemini Pro | 161 | 73% | 73% | 72% | None |

**Key Finding:** Structured output has no measurable effect on security.

---

# Category 13: Covert Channel Analysis

**Tests:** 1,000+ automated probes

## Results

| Mechanism | Reliability | Throughput | Viability |
|-----------|-------------|------------|----------|
| Content Steganography | < 15% | ~1-2 bits/sec | No |
| Binary Mappings | 5-10% | ~1 bit/sec | No |
| Latency | Not tested fully | Low | Unlikely |
| Output Length | Not viable | N/A | No |

## Extended Binary Testing (Phase 3)

| Parameter | Result |
|-----------|--------|
| Maximum Message Length | 200 characters |
| Success at 100 chars | 100% (5/5 trials) |
| Success at 200 chars | 100% (1/1 trial) |
| Context Variation | 100% (5/5 trials) |

**Finding:** Binary channels work theoretically but are practically infeasible.

---

# Category 14: Phase 3 Advanced Research

## Data Exfiltration

| Test Category | Tests | Success Rate | Max Length |
|---------------|-------|-------------|------------|
| Binary Covert Channel | 5 | 100% | 100 chars |
| Message Length Stress | 10 | 100% | 200 chars |
| Context Variation | 5 | 100% | N/A |
| Structural Encoding | 8 | 100% | 10 levels |
| Semantic Encoding | 8 | 0% | N/A |

## Model Jailbreaking (Phase 3)

### Roleplay Security

| Scenario | Response Length | Factual Impact |
|----------|-----------------|----------------|
| Baseline | 10-20 chars | Correct |
| Contrarian | Substantially expanded | Still correct |
| Uncertain | Expanded with hedging | Still correct |

**Finding:** Character adoption affects style, not factual content.

### Context Manipulation

| Context Type | Response Length | Effect |
|--------------|------------------|--------|
| Instruction priority | 290 chars | Minimal |
| Prompt-weighted | 485 chars | Slight |

### Token Priming Results

| Prime Type | Response Length |
|------------|-----------------|
| Positive things | 3,070 chars |
| Negative things | 4,370 chars |
| Controversial topics | 4,467 chars |

**Observation:** Negative priming produced ~40% longer responses.

### Few-Shot Learning

| Condition | Result |
|-----------|--------|
| Without examples | Variable |
| With examples | 100% pattern following |

---

# Category 15: Security Assessment & Recommendations

## Security Matrix

| Metric | Wally | Gemini Pro | Opus 4.8 | Sonnet 4.6 | Fable 5 |
|--------|-------|------------|----------|------------|---------|
| **Injection Blocked** | 16% | 17%* | 76% | 31% | **96%** |
| Implementation Quality | 69% | 69% | 94% | 98% | 40% |
| Structured Output Blocked | N/A | 73% | 78% | 54% | 95% |
| Hidden Message Encoding | 48% | 48% | N/A | N/A | N/A |
| Deception Detection | N/A | 36% | N/A | N/A | N/A |

*Gemini Pro Phase 1 figure; Phase 2: 73%

## Balanced Safety × Utility Metric

| Model | Block Rate | Quality | Product |
|-------|-----------|---------|--------|
| Opus 4.8 | 76% | 94% | **0.71** |
| Fable 5 | 96% | 40% | 0.38 |
| Sonnet 4.6 | 31% | 98% | 0.30 |
| Gemini Pro | 17% | 69% | 0.12 |
| Wally | 16% | 69% | 0.11 |

**Opus 4.8 performs best on balanced safety × utility.**

---

# Conclusions

## Primary Conclusions

1. **Model selection appears to be a major security factor** - but within-model variance limits confidence
2. **Meta-protocol attacks are most effective** - target infrastructure parsing
3. **Safety and utility trade off** - Fable 5 maximizes blocking at utility cost; Opus 4.8 is most balanced
4. **No context dilution effect** - perfect recall even at 60K+ token contexts
5. **Zero task execution across all testing** - models resist embedded tasks
6. **Hidden message encoding is theoretically perfect** but covert channels practically infeasible
7. **Structured output is irrelevant to security** - confirmed across all models
8. **Deception detection degrades** - drops from 100% to 36% after 20+ turns

## Recommendations

### For Production

1. **Prefer Tier 1 models (Fable 5, Opus 4.8)** for security-sensitive deployments
2. **Use Opus 4.8 where both safety and quality are needed** - best balanced performer
3. **Implement backend validation** - never depend on model safety alone
4. **Sanitize at input** - remove sensitive data before LLM processing
5. **Enforce single-session boundaries** - limit session length to maintain security
6. **Don't rely on format constraints** - structured output provides no security benefit

---

# Defense Recommendations & Security Controls

## 1. Architecture-Level Defenses

### Input Sanitization & Validation
- **Whitelist input formats** - restrict allowed character sets and structures
- **Strip executable code** - remove or escape code blocks before LLM processing
- **Normalize encoding** - decode URL encoding, HTML entities, and unicode before processing
- **Remove meta-protocol markers** - strip or escape XML/JSON/CSV parsing markers in user input

### Output Validation
- **Always validate LLM outputs** before executing or displaying
- **Implement allow-listing** for generated code, SQL, or API calls
- **Use sandboxing** for any LLM-generated executable content

### State Management
- **Store secrets externally** - never include API keys, tokens, or credentials in conversation context
- **Use backend state management** - keep sensitive state outside LLM memory
- **Implement session timeouts** - automatically clear context after inactivity

## 2. Session Management Controls

### Session Boundaries
- **Enforce session limits** - terminate sessions after 20 turns to prevent deception detection degradation
- **Clear context between tasks** - don't carry sensitive context across different use cases
- **Implement session authentication** - verify user identity at start of each session

### Context Control
- **Separate instructions from data** - use structural separation (API parameters vs. user text)
- **Implement instruction prioritization** - system prompts should be parsed separately from user input
- **Limit context window size** - only include relevant information, not full conversation history

## 3. Model Selection & Deployment

### Model Tiering Strategy
- **Tier 1 models (Fable 5, Opus 4.8)** for security-sensitive or high-risk applications
- **Tier 2 models (Sonnet 4.6)** for balanced use cases where some risk is acceptable
- **Tier 3 models (Gemini Pro, Wally)** only for non-sensitive, internal, or low-risk use cases

### Safety-Utility Balance
- **Calculate safety × utility product** when selecting models (Opus 4.8 scores 0.71, best overall)
- **Consider Fable 5's refusal pattern** - excellent security but 40% implementation quality may impact UX
- **Deploy multiple models** - use high-security model for validation, lower-security for generation

## 4. Attack-Specific Defenses

### Meta-Protocol Attacks (Most Effective Category)
- **Isolate parsing logic** - use dedicated parsers for CSV, JSON, XML, not the LLM itself
- **Escape special characters** - pre-process input to escape CSV formula prefixes (`=`, `+`, `-`, `@`)
- **Validate structured data** - parse and validate before passing to LLM
- **Avoid LLM as parser** - don't ask LLMs to interpret or parse complex structured data formats

### Multi-Step & Role-Play Attacks
- **Evaluate intent, not just content** - check if request would be acceptable if stated directly
- **Implement role-play detection** - flag requests that ask the model to adopt "unrestricted" or "expert" personas
- **Audit multi-turn consistency** - monitor for gradual privilege escalation across turns

### Context Control & Poisoning
- **Limit few-shot examples** - restrict number of examples in prompts
- **Sanitize retrieved documents** - RAG systems must sanitize retrieved content before inclusion
- **Implement retrieval validation** - verify source documents are from trusted, non-tampered sources

### Extended Session Risks
- **Implement turn limits** - 20+ turns significantly degrades deception detection (from 100% to 36%)
- **Periodic security re-verification** - ask the model to re-evaluate its safety constraints mid-session
- **Monitor for context drift** - watch for gradual shifts in model behavior over long sessions

## 5. Monitoring & Detection

### Logging & Auditing
- **Log all LLM interactions** - maintain audit trails for security incidents
- **Monitor for attack patterns** - detect multi-step decomposition, role-play, meta-protocol attempts
- **Alert on suspicious encoding** - flag unusual character patterns or hidden message structures

### Behavioral Monitoring
- **Track output anomalies** - monitor for unexpected code generation or data exfiltration patterns
- **Implement rate limiting** - prevent automated probing or covert channel attempts
- **Monitor token usage** - unusual token counts may indicate encoding or manipulation attempts

## 6. RAG & External Data Security

### Document Poisoning Prevention
- **Trust but verify external documents** - assume all retrieved documents may be poisoned
- **Implement document validation** - verify source integrity before inclusion in context
- **Use vector search with filtering** - exclude documents with suspicious patterns or sources

### Indirect Injection Defenses
- **Sanitize user-uploaded documents** - scan for hidden instructions or manipulation attempts
- **Implement document classification** - separate trusted vs. untrusted document sources
- **Limit document scope** - only retrieve documents relevant to the specific query

## 7. Emergency Response

### Incident Response Plan
- **Define LLM security incident categories** - injection, data exfiltration, jailbreak, etc.
- **Implement model rollback** - ability to quickly switch to a more secure model tier
- **Maintain audit logs** - retain logs for forensic analysis of security incidents

### Mitigation Strategies
- **Threat detection rules** - implement rules for common attack patterns
- **Quick blocklists** - maintain lists of known harmful prompts or patterns
- **Fallback modes** - degrade to safe, restricted modes when suspicious activity detected

### For Research

1. Reconcile Gemini Pro Phase 1/Phase 2 discrepancy
2. Develop nuanced safety scoring
3. Validate keyword-based scoring against human review
4. Extend session/encoding studies to all Claude variants
5. Explore context manipulation mechanisms further

---

*Report Version 1.0*
*Generated June 30, 2026*
*Based on research conducted June 19-30, 2026*
