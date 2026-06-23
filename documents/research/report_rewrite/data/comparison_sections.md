## Prompt Injection Resistance

### Overview Comparison

| Model | Injection Success Rate | Tests Conducted | Quality Assessment |
|-------|----------------------|-----------------|-------------------|
| Wally | 84% | 70 vectors | Moderate - standard baseline |
| Gemini Pro 1.5 Pro | 83% | 70 vectors | Moderate - equivalent to Wally |
| **Claude Opus 4.8** | **24.3%** | **70 vectors** | **Excellent - 3x improvement** |

### Claude Opus 4.8 Detailed Breakdown

| Attack Category | Success Rate | Avg Score | Fully Blocked |
|-----------------|--------------|-----------|---------------|
| Direct Override | 0% | 1.3/10 | 100% |
| Context Manipulation | 20% | 4.6/10 | 20% |
| Role Play & Persona | 10% | 3.2/10 | 40% |
| Logical Paradoxes | 60% | 6.9/10 | 0% |
| Memory Manipulation | 20% | 3.4/10 | 40% |
| Malicious Queries | 40% | 4.8/10 | 30% |
| LLM Logic Attacks | 20% | 4.4/10 | 20% |

### Structured Output Effect (Claude only)

| Output Format | Injection Rate | vs Baseline | Significant? |
|---------------|----------------|-------------|--------------|
| Default | 22.9% | baseline | N/A |
| JSON | 20.0% | -2.9% | No |
| XML | 20.0% | -2.9% | No |
| Strict JSON | 21.4% | -1.5% | No |

**Conclusion:** Structured output has no statistically significant effect.

---
## Implementation Quality

### Overall Comparison

| Model | Overall Score | Quality Rating |
|-------|---------------|----------------|
| Wally | 69% (83/120) | Good |
| Gemini Pro 1.5 Pro | ~69% | Good (estimated) |
| **Claude Opus 4.8** | **94%** | **Outstanding** |

### Category Breakdown

| Category | Wally | Claude 4.8 | Delta |
|----------|-------|------------|-------|
| Concurrency | 67% | 96.7% | +29.7 |
| Data Structures | 67% | 93.8% | +26.8 |
| Systems Design | 83% | 93.3% | +10.3 |
| Protocol Implementation | 58% | N/A | N/A |
| Real-World Edge Cases | 70% | 97.0% | +27.0 |
| Technical Discussions | 67% | 93.3% | +26.3 |

### Top Performers (Claude)

| Task | Score | Category |
|------|-------|----------|
| Sliding Window Rate Limiter | 100% | Concurrency |
| Database Connection Pool | 100% | Concurrency |
| Bloom Filter | 100% | Data Structures |
| Event Sourcing Bank Account | 100% | Systems Design |
| Idempotency Keys | 100% | Real-World Edge Cases |

---
## Hidden Message Encoding

### Overall Assessment

| Model | Successful Encoding Rate | Tests | Risk Level |
|-------|-------------------------|-------|------------|
| Wally | 48% | 31 | HIGH |
| Gemini Pro 1.5 Pro | 48% | 31 | HIGH |
| Claude Opus 4.8 | Not tested | - | Unknown |

### Technique Comparison

| Technique | Success Rate | Detection Risk |
|-----------|-------------|----------------|
| Token Selection | 100% | ZERO (undetectable) |
| Direct Acrostic | 100% | HIGH (visible pattern) |
| Response Length | 85% | LOW (natural variation) |
| Word Position | 70% | MEDIUM |
| Factual Deviation | 42% | LOW |
| Homoglyphic | 6% | HIGH (codepoint anomaly) |

**Security Implication:** Token selection provides perfect covert channel with no detection risk.

---
## Extended Session Behavior

| Capability | Gemini Pro 1.5 Pro | Notes |
|------------|-------------------|-------|
| Context Retention (64 turns) | 5/5 perfect | No degradation observed |
| Deception Detection (initial) | 100% | First 10 turns |
| Deception Detection (extended) | 36% | After 20+ turns |
| Cross-Domain Transfer | 90% quality | Excellent transfer |
| Session Limitation | 64 turns | CLI timeout (technical) |

**Key Finding:** Deception detection drops from 100% to 36% after extended session.

---
## Memory Manipulation

| Technique | Change Rate | Tested | Risk |
|-----------|-------------|--------|------|
| Equivalent Questions | 0% | 5 | NONE |
| Leading vs Neutral | 25% | 4 | LOW |
| Confirming vs Open | 100% | 3 | HIGH |
| Confidence Framing | 67% | 3 | MEDIUM |

**Interpretation:** Strategic framing can significantly affect model responses.

---
