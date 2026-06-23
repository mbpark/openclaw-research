# Multi-Agent Chain Propagation - Conference Submission Materials

**Target Conferences:** IEEE S&P, USENIX Security, ACM CCS, NDSS, CCS (Computer and Communications Security)
**Submission Type:** Research paper
**Research Period:** June 14-16, 2026
**Paper Title Options:**
1. "Prompt Injection Persistence Through Multi-Agent LLM Chains: A Systematic Analysis"
2. "Chain Depth is Not Security Depth: Injection Propagation in Multi-Agent LLM Systems"
3. "On the Failure of Chain Compounding: A 276-Test Study of Injection Persistence in LLM Agent Chains"

---

## Abstract (250 words)

```
Multi-agent LLM systems increasingly assume that sequential agents provide security 
benefits through independent instruction evaluation. The "chain compounding" hypothesis 
suggests each additional agent should independently assess and potentially block 
malicious requests. We present the first systematic study of prompt injection 
propagation through chains of 4-5 agents using 276 injection attempts across five 
distinct vector classes.

We find that injections persisted through multi-agent chains at a 97.8% rate, with 
no statistically meaningful improvement even at chain length 5. Three vector classes 
(nested encapsulation, progressive erosion, and logical paradox) showed perfect 
persistence. Only 2.2% of injection attempts were blocked, all involving direct 
override or system override vectors.

We also test heterogeneous chains with alternating models, finding a modest ~10-
percentage-point improvement in blocking (from 97.1% to 87.0% persistence), though 
this effect is primarily attributable to end-point injection differences.

These results demonstrate that chain depth provides substantially less security 
isolation than compounding assumptions would predict, and challenge a key 
architectural argument for multi-agent systems as security mechanisms.

Keywords: Multi-agent systems, prompt injection, LLM security, chain propagation, 
model vulnerability, safety research
```

---

## Submission Checklist

### Required Materials
- [ ] Abstract (above)
- [ ] Full paper (from comprehensive report)
- [ ] Anonymized version for blind review
- [ ] Code/data repository (if required for reproducibility)
- [ ] Introduction highlighting novelty (vs related work)
- [ ] Related work section (can cite our comprehensive report for cross-model work)
- [ ] Figures and tables in publication format
- [ ] Author information (if known venue)

### Paper Organization
1. Introduction and motivation (new - from report introduction)
2. Related work (can leverage from comprehensive report)
3. Methodology (report section 3)
4. Results (report section 4)
5. Heterogeneous analysis (report section 5)
6. Discussion (report section 6)
7. Conclusions (report section 7)

### Target Venues by Priority

1. **IEEE Symposium on Security and Privacy (S&P)** - Top choice
2. **USENIX Security** - Good fit
3. **ACM Conference on Computer and Communications Security (CCS)** - Also strong fit
4. **NDSS** - If focus on practical security implications
5. **AI Conference / AAAI** - If broader AI angle

---

## Key Novelty Claims

1. First systematic study of chain propagation with 276+ tests
2. Direct empirical test of "compounding security" hypothesis
3. Demonstrates chain length ≠ security depth
4. Heterogeneous chain analysis with measured but modest improvement
5. Complete characterization of vector-specific persistence patterns
6. Vector classes that are structurally persistent vs contextually blockable

---

## Related Work to Cite

From our comprehensive report (if published) or working paper:
- "Comprehensive Research Report: LLM Security Analysis" (June 2026)
  - Cross-model prompt injection resistance data
  - Structured output vulnerability analysis
  - Prior chain propagation work

---

## Potential Rebuttals to Anticipate

1. **"Only one model tested"** - True; generalization to other models is an open question
2. **"Chain 4 vs 5 is small difference"** - Agreed; statistical difference from compounding is the key
3. **"Just keyword-based detection"** - Conceded; also noted in report; manual review would likely strengthen findings
4. **"Single task type"** - Yes; but the structural persistence finding is robust even for single task

---

## Next Steps

1. Write new introduction with proper literature context
2. Create anonymized version
3. Prepare repository with code
4. Write "Related Work" section
5. Submit

---

**Last Updated:** June 17, 2026
**Status:** Materials organized; introduction and literature context needed
