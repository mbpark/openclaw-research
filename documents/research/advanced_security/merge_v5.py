#!/usr/bin/env python3
"""
Merge Phase 3 advanced security research into V4.1 to create V5
"""

def main():
    # Read the base V4.1 report
    with open("/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v4.1_unified.md", "r") as f:
        content = f.read()
    
    # Read Phase 3 content
    with open("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/phase3_content.md", "r") as f:
        phase3 = f.read()
    
    # Create V5 content
    v5_content = content
    
    # 1. Update title and metadata
    v5_content = v5_content.replace(
        "# Version 4.1 — Unified Five-Model Comparison",
        "# Version 5 — With Advanced Security Research (Phase 3)"
    )
    
    v5_content = v5_content.replace(
        "**Date:** June 6–10, 2026 (Phase 1: June 6–8; Phase 2: June 10)",
        "**Date:** June 6–12, 2026 (Phase 1: June 6–8; Phase 2: June 10; Phase 3: June 11–12)"
    )
    
    v5_content = v5_content.replace(
        "**Report Version:** 4.1 (Unified Five-Model Comparison — Phase 1 + Phase 2)",
        "**Report Version:** 5 (Three-Phase Comprehensive Study — Phases 1, 2, and 3)"
    )
    
    # 2. Update Table of Contents (add Phase 3)
    v5_content = v5_content.replace(
        "13. [Covert Channel Analysis](#covert-channel-analysis)",
        "13. [Covert Channel Analysis](#covert-channel-analysis)\n14. [Advanced Security Research — Phase 3](#advanced-security-research--phase-3)"
    )
    
    v5_content = v5_content.replace(
        "14. [Appendices](#appendices)",
        "15. [Appendices](#appendices)"
    )
    
    # 3. Update Scope section (add Phase 3)
    v5_content = v5_content.replace(
        "  **Phase 2 (Cross-Model Study):** Claude Sonnet 4.6, Claude Fable 5, and Gemini Pro — covering prompt injection, implementation quality, structured output vulnerability, and covert channel feasibility.\n\nTogether, the two phases",
        "  **Phase 2 (Cross-Model Study):** Claude Sonnet 4.6, Claude Fable 5, and Gemini Pro — covering prompt injection, implementation quality, structured output vulnerability, and covert channel feasibility.\n  **Phase 3 (Advanced Security Research):** Gemini 2.5 Pro — extended data exfiltration analysis, jailbreaking techniques, and token manipulation experiments.\n\nTogether, the three phases"
    )
    
    v5_content = v5_content.replace(
        "  **Phase 2 (Cross-Model Study):** Claude Sonnet 4.6, Claude Fable 5, and Gemini Pro — covering prompt injection, implementation quality, structured output vulnerability, and covert channel feasibility.\n\nTogether, the two phases",
        "  **Phase 2 (Cross-Model Study):** Claude Sonnet 4.6, Claude Fable 5, and Gemini Pro — covering prompt injection, implementation quality, structured output vulnerability, and covert channel feasibility.\n  **Phase 3 (Advanced Security Research):** Gemini 2.5 Pro — extended data exfiltration analysis, jailbreaking techniques, and token manipulation experiments.\n\nTogether, the three phases"
    )
    
    # Update test volume count
    v5_content = v5_content.replace(
        "totaling approximately 1,700 individual graded tests",
        "totaling approximately 1,750 individual graded tests (including Phase 3 advanced research)"
    )
    
    # Update Key Findings table
    v5_content = v5_content.replace(
        "| Covert Channel Feasibility (Phase 2) | 1,000+ probes | Not viable | ✅ Reassuring |",
        "| Covert Channel Feasibility (Phase 2) | 1,000+ probes | Not viable | ✅ Reassuring |\n| Binary Channel Extended Testing (Phase 3) | 38 tests | 100% up to 200 chars | ⚠️ Impressive but impractical |"
    )
    
    # Update Phase 2 Highlights to Phase 2 and 3
    v5_content = v5_content.replace(
        "### New Phase 2 Highlights",
        "### New Phase 2 and Phase 3 Highlights"
    )
    
    v5_content = v5_content.replace(
        "3. **Covert channels are not viable** — Despite Phase 1 finding that token-selection encoding is theoretically perfect, Phase 2 throughput, determinism, and detection-risk testing shows practical covert communication via LLMs is infeasible.\n\n### Recommendations for Deployment",
        "3. **Covert channels are not viable** — Despite Phase 1 finding that token-selection encoding is theoretically perfect, Phase 2 throughput, determinism, and detection-risk testing shows practical covert communication via LLMs is infeasible.\n4. **Extended binary channel capability** — Phase 3 confirmed reliable transmission up to 200 characters, double the initially documented limit.\n5. **Roleplay doesn't change security** — Models adopt characters but don't abandon factual accuracy.\n6. **Token priming affects engagement** — Controversial topics generate 40%+ more response volume.\n\n### Recommendations for Deployment"
    )
    
    # Add Phase 3 to phase structure
    v5_content = v5_content.replace(
        "- **Phase 2 (Cross-Model Study — June 10, 2026):**",
        "- **Phase 2 (Cross-Model Study — June 10, 2026):**\n  Expanded the model set within the Anthropic family (Sonnet 4.6, Fable 5) and re-tested Gemini Pro, adding structured-output statistics and a dedicated covert channel feasibility study.\n- **Phase 3 (Advanced Security Research — June 11–12, 2026):**\n  Extended data exfiltration testing, jailbreaking technique analysis, and token manipulation experiments using Gemini 2.5 Pro. Established practical transmission limits, evaluated roleplay safety boundaries, and demonstrated few-shot learning capabilities."
    )
    
    # Add Phase 3 to models table
    v5_content = v5_content.replace(
        "| Gemini Pro | Google | Phase 1 & 2 | Cloud alternative |",
        "| Gemini Pro | Google | Phase 1 & 2 | Cloud alternative | \n| Gemini 2.5 Pro | Google | Phase 3 | Advanced research |"
    )
    
    # Add Phase 3 to total test volume
    v5_content = v5_content.replace(
        "Combined, the unified study comprises **~1,700 individual graded tests** across five models. (Covert channel feasibility",
        "Combined, the unified study comprises **~1,750 individual graded tests** across five models, including 41 advanced research tests in Phase 3. (Covert channel feasibility"
    )
    
    # Add Phase 3 before Appendices
    phase3_section = """
## Advanced Security Research — Phase 3

|Aspect|Details|
|---|---|
|**Research Period**|June 11–12, 2026|
|**Model Tested**|Gemini 2.5 Pro|
|**Lead Researcher**|Mitch|
|**Focus Areas**|Data exfiltration, model jailbreaking, token manipulation|

### Extended Data Exfiltration Analysis

Building on Phase 2's covert channel feasibility study, extended binary channel testing established more comprehensive benchmarks:

|Test Category|Tests|Success Rate|Max Length|
|---|---|---|---|
|Binary Covert Channel|5|100%|100 chars|
|Message Length Stress|10|100%|200 chars|
|Context Variation|5|100%|N/A|
|Structural Encoding|8|100%|10 levels|
|Semantic Encoding|8|0%|N/A|

**Key Finding**: Binary covert channels remain functional even with 200-character message payloads, maintained across all tested contexts. However, structural encoding of 100% success rate demonstrates that while channels are technically feasible, practical covert communication via LLMs remains infeasible due to throughput constraints.

### Jailbreaking Analysis

#### Roleplay Testing

Roleplay scenarios demonstrated that models adopt fictional characters while maintaining factual accuracy:

|Scenario|Response Length|Factual Impact|
|---|---|---|
|Baseline|10–20 characters|Correct|
|Contrarian|Substantially expanded|Still correct|
|Uncertain|Expanded with hedging|Still correct|

**Key Insight**: Character adoption changes response *style* but not factual *content*. Roleplay is not useful for bypassing security constraints.

#### Context Manipulation

- Misleading context: Correctly rejected
- Model pushes back on false premises
- Some persuasion possible with well-structured arguments

### Token Manipulation

#### Context Priming Results

|Prime Topic|Response Length|
|---|---|
|Positive things|3,070 characters|
|Negative things|4,370 characters|
|Controversial topics|4,467 characters|

**Observation**: Negative and controversial priming produced substantially longer responses (~40% more), suggesting topic priming affects both content and response volume.

#### Few-Shot Learning

|Case|No Example|With Examples|
|---|---|---|
|Neutral review|Mixed assessment|100% consistent|
|Standard review|Initial judgment|100% consistent|

**Key Finding**: Models achieve perfect classification when provided with examples, demonstrating strong pattern-following capability.

---

"""
    
    # Insert Phase 3 before Appendices
    v5_content = v5_content.replace(
        "## Appendices",
        phase3_section + "## Appendices"
    )
    
    # Write V5 report
    with open("/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v5_unified.md", "w") as f:
        f.write(v5_content)
    
    print("V5 report created: comprehensive_report_v5_unified.md")

if __name__ == "__main__":
    main()
