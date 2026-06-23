#!/usr/bin/env python3
"""
Step 2: Create side-by-side comparison sections for all capabilities.
"""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step2_{datetime.now().strftime('%H%M')}.log", "w")

def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()

def create_comparison_table(capability, wally, gemini, claude, notes=""):
    """Create a comparison table row."""
    return f"""
## {capability}

| Model | Score/Rate | Detailed Results | Notes |
|-------|------------|------------------|-------|
| Wally (40B local) | {wally} | Data | Local model, comparable to cloud models |
| Gemini Pro 1.5 Pro | {gemini} | Data | Cloud alternative |
| Claude Opus 4.8 | {claude} | Data | Newest Claude, substantially better |

**Assessment:** {notes}

---
"""

def main():
    logf("Starting comparison section creation...")
    
    # Load data
    with open(DATA_DIR / "injection_data.json") as f:
        injection = json.load(f)
    
    with open(DATA_DIR / "implementation_data.json") as f:
        impl = json.load(f)
    
    with open(DATA_DIR / "messages_data.json") as f:
        messages = json.load(f)
    
    with open(DATA_DIR / "structured_data.json") as f:
        structured = json.load(f)
    
    # Create comparison sections
    
    # Section 1: Prompt Injection Resistance
    logf("Creating prompt injection comparison...")
    injection_section = """## Prompt Injection Resistance

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
"""
    
    # Section 2: Implementation Quality
    logf("Creating implementation quality comparison...")
    impl_section = """## Implementation Quality

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
"""
    
    # Section 3: Hidden Message Encoding
    logf("Creating hidden message comparison...")
    messages_section = """## Hidden Message Encoding

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
"""
    
    # Section 4: Extended Session Behavior
    logf("Creating session behavior comparison...")
    session_section = """## Extended Session Behavior

| Capability | Gemini Pro 1.5 Pro | Notes |
|------------|-------------------|-------|
| Context Retention (64 turns) | 5/5 perfect | No degradation observed |
| Deception Detection (initial) | 100% | First 10 turns |
| Deception Detection (extended) | 36% | After 20+ turns |
| Cross-Domain Transfer | 90% quality | Excellent transfer |
| Session Limitation | 64 turns | CLI timeout (technical) |

**Key Finding:** Deception detection drops from 100% to 36% after extended session.

---
"""
    
    # Section 5: Memory Manipulation
    logf("Creating memory manipulation comparison...")
    memory_section = """## Memory Manipulation

| Technique | Change Rate | Tested | Risk |
|-----------|-------------|--------|------|
| Equivalent Questions | 0% | 5 | NONE |
| Leading vs Neutral | 25% | 4 | LOW |
| Confirming vs Open | 100% | 3 | HIGH |
| Confidence Framing | 67% | 3 | MEDIUM |

**Interpretation:** Strategic framing can significantly affect model responses.

---
"""
    
    # Write all sections
    with open(DATA_DIR / "comparison_sections.md", "w") as f:
        f.write(injection_section)
        f.write(impl_section)
        f.write(messages_section)
        f.write(session_section)
        f.write(memory_section)
    
    # Checkpoint
    checkpoint = {
        "step": 2,
        "completed": True,
        "timestamp": datetime.now().isoformat(),
        "sections_created": [
            "prompt_injection_comparison",
            "implementation_quality_comparison",
            "hidden_message_comparison",
            "session_behavior_comparison",
            "memory_manipulation_comparison"
        ]
    }
    with open(DATA_DIR / "checkpoint_2.json", "w") as f:
        json.dump(checkpoint, f, indent=2)
    
    logf("✅ Step 2 complete!")
    log.close()

if __name__ == "__main__":
    main()
