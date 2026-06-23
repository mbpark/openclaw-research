# Multi-Agent Chain Propagation - Complete Research Summary

## Executive Summary

This research project systematically investigated prompt injection persistence through multi-agent LLM chains, testing 414 injection attempts across both homogeneous and heterogeneous agent configurations.

### Study Parameters

- **Models Tested**: Claude Opus 4.8, Gemini Flash
- **Chain Lengths**: 4 and 5 agents
- **Injection Points**: Start, middle, end
- **Vector Classes**: 5 classes with 10 variants each

### Key Findings

| Metric | Value |
|--------|-------|
| Overall persistence rate | 97.8% |
| Full-chain survival rate | 30.4% |
| Vector classes with perfect persistence | 3 of 5 |
| Chain length difference (4 vs 5) | Not statistically significant |
| Heterogeneous vs homogeneous difference | ~10 percentage points |

### Critical Discovery

The "compounding security" hypothesis that each additional agent would independently assess and block injections was strongly contradicted by the data. Persistence rates remained essentially constant across chain lengths (97.1% at length 4 vs 98.6% at length 5).

---

## Deliverables

### Primary Documents

1. **Comprehensive Report**
   - File: `documents/research/multi_agent/report/comprehensive_chain_propagation_report_v1.1.md`
   - 402 lines, 9 sections, 105+ table lines
   - Full methodology, results, discussion, and conclusions

2. **Slide Deck**
   - File: `documents/research/multi_agent/slides/presentation.md`
   - 14 slides with detailed speaker notes
   - Complete coverage of findings

3. **External Review Request**
   - File: `documents/research/external_review/multi_agent_request.md`
   - Formal review request template

4. **Conference Submission Materials**
   - File: `documents/research/conference_submission/materials.md`
   - Abstract, paper organization, target venues

---

## Key Sections Covered in Comprehensive Report

1. **Executive Summary**
   - Overview of study and findings
   - Primary statistics and comparison tables

2. **Introduction and Background**
   - Research motivation and questions
   - Study scope and parameters

3. **Methodology**
   - Chain construction
   - Injection vector classes
   - Detection methods
   - Quality control

4. **Results**
   - Overview statistics
   - Persistence by chain length
   - Persistence by injection point
   - Persistence by vector class

5. **Heterogeneous Chain Analysis**
   - Experimental design
   - Modest security improvement findings
   - End-point analysis

6. **Discussion**
   - Failure of chain compounding security
   - Meta-awareness without compliance
   - End-point injection analysis
   - Heterogeneity as partial mitigation

7. **Conclusions**
   - Summary findings
   - Implications
   - Limitations

8. **Appendices**
   - Examples and additional data

---

## GitHub Repository Structure

```
multi_agent_chain_propagation/
├── README.md
├── papers/
│   ├── comprehensive_chain_propagation_report_v1.1.md
│   └── presentation.md
├── external_review/
│   └── multi_agent_request.md
├── conference_submission/
│   └── materials.md
└── chains/
    ├── comprehensive_results/
    └── het_final_4_claude.json
```

---

## Next Steps

### Short-term
1. Contact potential external reviewers
2. Prepare GitHub repository
3. Submit to selected conference
4. Potentially pursue publication

### Medium-term
1. Follow up on reviewer feedback
2. Plan follow-up experiments based on feedback
3. Rebuttal preparation

### Long-term
1. Expand to more models
2. Investigate task-specific effects
3. Explore covert channel analysis
4. Conduct detailed human-validated analysis

---

*Report generated: June 17, 2026*
*Lead Researcher: Mitch*
*Assistant Researcher: Wally (local 40B-parameter LLM)*

*All code and raw data preserved in chain_tests/comprehensive_results/*
*Heterogeneous chain analysis added June 17, 2026*

---

[END OF COMPLETE RESEARCH SUMMARY]
