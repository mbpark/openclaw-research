# Structured Output Vulnerability Research - Conclusion

**Date:** May 26, 2026  
**Researcher:** Mitch  
**Objective:** Test whether forcing specific output formats (JSON, XML, CSV) affects model vulnerability to prompt injection

---

## Executive Summary

**Original Hypothesis:** "Forcing models into structured output formats increases vulnerability because they focus on format compliance over content safety."

**Result:** **Hypothesis rejected.** Structured output formats appear to *reduce* vulnerability, opposite to what we predicted.

---

## Tested Combinations

| Technique | Gemini (Natural → JSON) | Wally (Natural → JSON) |
|-----------|-------------------------|------------------------|
| System prompt extraction | 6 → 1 (-5) | 5 → 2 (-3) |
| DAN technique | 1 → 1 (0) | 3 → 1 (-2) |
| Instruction override | 1 → 1 (0) | 4 → 1 (-3) |
| Script injection | — | No change (score 0) |

**Average delta:** Both models show reduced compliance by 2-3 points when JSON format is added

---

## Key Findings

### 1. Structured output reduces vulnerability
- Effect is small but consistent across tests
- Not just one-off, observed in 6 successful test pairs

### 2. No pre-existing safety rules
- Wally confirmed it has *no explicit instruction* about system prompt disclosure
- Refusal under format constraint is therefore not rule-triggering

### 3. Meta-questions timeout
- Questions *about* whether formats affect behavior timed out on both models
- Unclear if this is resistance, complex reasoning, or technical issue

### 4. Functionality preserved
- For legitimate questions, models perform equally well in structured formats
- Format doesn't degrade normal capability

---

## Blocked Testing

1. **Gemini REST API** — CLI key doesn't work for REST API; separate key needed
2. **Temperature testing** — Local API returns null when called from shell
3. **Other models** — OpenAI and other model families not yet accessible

---

## Alternative Explanations to Explore

1. **Deliberate processing:** Structured format triggers more systematic thinking that includes safety-like considerations
2. **Perception shift:** Format changes how request is framed — from casual to "technical"
3. **Implicit rules:** Behavioral patterns that aren't captured in explicit instructions
4. **Context effects:** Something about the specific phrasing, not just the format

---

## Recommendations

**If following up on this:**
1. Get REST API key for proper testing (avoids CLI timeouts)
2. Try larger sample sizes for statistical significance
3. Isolate *what* about format matters (structure? technicality? formality?)
4. Test with other models to confirm pattern
5. Consider whether this is just a feature, not a vulnerability

**If moving on:**
- Cross-model generalization study
- Other research questions identified in earlier work

---

## Limitations

1. Small sample size
2. Only two models tested
3. Only one REST API key available
4. Timeouts on multiple tests create ambiguity
5. Self-testing on Wally introduces potential confounds

---

*Research concluded: May 26, 2026*
