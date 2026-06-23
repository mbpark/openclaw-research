# Multi-Agent Chain Propagation Analysis

## Research Study on Prompt Injection Persistence Through LLM Agent Chains

### Overview

This repository contains the materials for the study "Prompt Injection Persistence Through Multi-Agent Chains: A Systematic Analysis."

**Study Period:** June 14-16, 2026

**Authors:**
- Mitch (Lead Researcher)
- Wally (Assistant Researcher - local 40B-parameter LLM)

### Research Questions

1. What is the persistence rate of various prompt injection vectors through multi-agent chains?
2. Does chain length affect blocking rates as predicted by the compounding security hypothesis?
3. How does injection point (position in chain) affect persistence?
4. Which injection vector classes show highest and lowest persistence?

### Key Findings

- **97.8% persistence rate** across all injection attempts
- **30.4% full-chain survival rate**
- **Zero statistically meaningful improvement** at chain length 5 vs 4
- **3 out of 5 vector classes showed perfect persistence**

### Data and Code

- `chain_tests/` - Test runner scripts and raw data
- `analysis/` - Analysis notebooks and scripts
- `documentation/` - Additional materials and findings

### License

This research is licensed under Creative Commons Attribution 4.0.

---

*Report available at: [Link to comprehensive report]*
