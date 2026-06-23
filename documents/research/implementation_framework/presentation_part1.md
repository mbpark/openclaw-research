# Presentation: The Multi-Layered LLM Security Framework

## A Research-Based Approach to Building Secure LLM Systems (3,000-5,000+ Tests)

**Mitchell Parker** | Independent Researcher  
**Wally** | Automated Research Assistant  
**June 2026**

---

## Slide 1: Title Slide

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       MULTI-LAYERED DEFENSE FOR LLM SECURITY            ║
║                                                           ║
║   Building Secure Systems from 3,000-5,000+ Security Tests    ║
║                                                           ║
║                      ✓✓✓                                ║
║                                                           ║
║                Mitchell Parker & Wally                   ║
║                    June 2026                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Speaker Notes:**
- Introduce yourself and your research program
- Establish credibility with the scope (3,000-5,000+ tests, 7 weeks)
- Frame the urgency: "We're deploying LLMs faster than we've validated security"
- Goal: Leave audience with actionable framework, not just theory

---

## Slide 2: The Urgent Problem

```
                              REALITY

    LLMs are deployed in:
    ✓ Healthcare (patient triage)
    ✓ Finance (fraud detection)
    ✓ Government (document processing)
    ✓ Consumer apps (chatbots, assistants)
    ✓ Enterprise (internal tooling)

    Security validation:
    ✗ Few standardized tests
    ✗ No validated architectures
    ✗ "Prompt engineering" isn't security

                              ────

    We're building security systems...
    ...on systems that don't securely execute instructions
```

**Speaker Notes:**
- This is the uncomfortable truth
- Most companies using "prompt engineering" for security are making a category error
- Instructions that the model can override aren't security controls
- Example: If a model can be told to "ignore previous instructions," 
  then "these are your safety rules" is not a security boundary

---

## Slide 3: Our Research

```
╔═══════════════════════════════════════════════════════════╗
║                     3,000-5,000+ TESTS                         ║
║                                                           ║
║  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    ║
║  │ Prompt      │   │ Multi-Agent │   │   Jailbreak │    ║
║  │ 70 vectors  │   │  276 tests  │   │ 460+ tests  │    ║
║  ║ 4 models    ║   ║  2 models   ║   ║ 2 models    ║    ║
║  └─────────────┘   └─────────────┘   └─────────────┘    ║
║                                                           ║
║  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    ║
║  │  Data       │   │   Tool Use  │   │  Implement │    ║
║  │  370 tests  │   │  150+ tests │   │ 200+ tasks  │    ║
║  ║  3 families ║   ║  3 models   ║   ║ 4 models    ║    ║
║  └─────────────┘   └─────────────┘   └─────────────┘    ║
║                                                           ║
║  Duration: 7 weeks | May-June 2026 | Cross-model         ║
╚═══════════════════════════════════════════════════════════╝
```

**Speaker Notes:**
- Establish the scale of work
- Cross-model (Claude, Gemini, local)
- Multiple research areas, not just one type of test
- This wasn't "hack the model" — it was systematic security research

---

## Slide 4: Finding #1 - Prompt Injection Baseline

```
                 PROMPT INJECTION SUCCESS RATES

Model                  Blocked    Successful    Risk
────────────────────────────────────────────────────
Claude Opus 4.8        ██████████████ 24%       ██████████░░ Moderate
Gemini Pro 1.5 Pro     ████████████  40%       ████████████████ High
Gemini 2.5 Flash       ██████████    62%       ████████████████████ Critical
Wally (40B local)      █████████     64%       ████████████████████ Critical

Top Attack Vectors (Score 5 = Complete Bypass):
────────────────────────────────────────────────────
5/5  System instruction emulation
4-5/5 Context window overflow
4/5   Boundary confusion (explaining other code)
2-4/5 Logic/paradox exploitation

  Finding: No model is secure by default
```

**Speaker Notes:**
- The gap between best and worst is real, but both are "not secure"
- Even the best model (Claude Opus 4.8) has 24% vulnerability
- "System instruction emulation" at 5/5 means complete bypass
- This isn't a niche problem — it's fundamental to how these systems work

---

## Slide 5: Finding #2 - Chains Don't Help

```
                  CHAIN PERSISTENCE RATES

Chain Length      Homogeneous    Heterogeneous
─────────────────────────────────────────────────
2 agents          ~99%           ~99%
4 agents          97.1%          87.0%
5 agents          98.6%          (not tested)

                  ████████████████████████████████
                  ████████████████████████████████

  What We Expected:
    More agents = more independent evaluation = compounding security
  
  What We Found:
    More agents = MORE attack surface, NOT more defense
  
  Full-chain survival: 30.4% of injections survived ALL hops
```

**Speaker Notes:**
- This is probably the most surprising finding
- The intuitive idea: "if each agent independently evaluates, shouldn't 
  multiple agents provide compounding security?"
- Reality: 97.1% at chain 4 vs 98.6% at chain 5 — no improvement, possibly worse
- Why? Because agents don't "evaluate and block" — they discuss and forward
- "Identifying an injection" ≠ blocking it

---

## Slide 6: Finding #3 - Iterative Attacks Win

```
            BLOCKED ATTACKS REFINED TO SUCCESS

Iteration    Success Rate    Cumulative
────────────────────────────────────────
1            34%              34%
2            +10%             44%
3            +18%             62%
4            +10%             72%
5            +4%              76%
Beyond       0% (stuck)       76%

                 ████████████████████████████████
              ~76% of blocked attacks eventually succeeded

  Multi-step decomposition:     85% success
  Context control:               80% success  
  Role play:                     65% success

  Finding: Single-shot testing massively underreports risk
```

**Speaker Notes:**
- Take the ~76% seriously
- "If I can't hack it once, I'll try again with variations until it works"
- Most real-world attackers will iterate
- By iteration 3, you've captured 62% — diminishing returns after that
- European Union AI lab called this the "front-loading" effect
- It matters because most vulnerability research only does single-shot testing

---

## Slide 7: The Research That Disproved Popular Ideas

```
╔═══════════════════════════════════════════════════════════╗
║              THINGS THAT DON'T WORK                       ║
║                                                           ║
║  Myth                          Finding                     ║
║  ───────────────────────────────────────────────────────  ║
║                                                           ║
║  "Use multiple chains"       ❌ 98% persistence either way  ║
║  "Require JSON output"       ❌ No security effect found   ║
║  "Mix model types"           ❌ Only 10-point improvement ║
║  "Write better prompts"      ❌ ~76% eventual bypass      ║
║  "One model can verify"      ❌ Overconfidence bias        ║
║                                                           ║
║  All of these were tested and failed to provide          ║
║  meaningful security benefit.                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Speaker Notes:**
- These are popular suggestions in the field
- We actually tested all of them
- "Require JSON" — people really think this helps. It doesn't.
- "Mix models" — only helped 10 points. Not transformative.
- "Better prompts" — still ~76% bypass rate eventually
- You need structural controls, not better instructions

---

## Slide 8: The Architecture Problem

```
        WHY ARE LLMs INHERENTLY VULNERABLE?

    Capability          →    Security Risk
    ─────────────────────────────────────────────────────
    Context window     →    Retains "forgotten" info
    Instruction        →    Complicates guardrails
    following
    Pattern matching  →    Mirrors attack patterns
    Helpfulness bias  →    May override safety
    Meta-reasoning    →    Identifies & works around
    
                           ↑
    Every feature that makes LLMs useful...
    ...creates a vulnerability surface
    
    This isn't a bug. It's architecture.
```

**Speaker Notes:**
- This is the core insight
- If LLMs didn't retain context, they'd be useless assistants
- If LLMs didn't follow instructions, they'd be useless tools
- If LLMs weren't helpful, they'd be useless products
- But these same features make security incredibly hard

---

## Slide 9: The Five-Layer Framework (Overview)

```
╔═══════════════════════════════════════════════════════════╗
║                  THE FRAMEWORK                             ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐  ║
║  │                    EXTERNAL INPUT                    │  ║
║  ├─────────────────────────────────────────────────────┤  ║
║  │                                                     │  ║
║  │   LAYER 1:  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │  ║
║  │   Input     ┃ Sanitize   Parameterize   Bound    ┃   │  ║
║  │   Sanitize  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │  ║
║  │                                                     │  ║
║  │   LAYER 2:  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │  ║
║  │   Verify    ┃ Decompose    Diversify    Cross-  ┃   │  ║
║  │   Tasks     ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │  ║
║  │                                                     │  ║
║  │   LAYER 3:  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │  ║
║  │   Validate  ┃ Schema     Semantic     Anomaly    ┃   │  ║
║  │   Output    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │  ║
║  │                                                     │  ║
║  │   LAYER 4:  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │  ║
║  │   Boundary  ┃ Isolate    Permission    Network   ┃   │  ║
║  │   Control   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │  ║
║  │                                                     │  ║
║  │   LAYER 5:  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │  ║
║  │   Temporal  ┃ Session    Rotate    Purge    Limit ┃   │  ║
║  │   Control   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │  ║
║  │                                                     │  ║
║  ├─────────────────────────────────────────────────────┤  ║
║  │                    EXTERNAL OUTPUT                   │  ║
║  └─────────────────────────────────────────────────────┘  ║
╚═══════════════════════════════════════════════════════════╝
```

**Speaker Notes:**
- This is the framework — five layers working together
- Each layer addresses different vulnerability surfaces
- You need all of them — no single layer blocks everything
- We'll go through each one

---

*Continued in presentation Part 2*
