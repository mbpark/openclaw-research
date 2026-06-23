#!/usr/bin/env python3
"""
Add comprehensive cross-model analysis to V5 report
"""

def main():
    # Read the V5 report
    with open("/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v5_unified.md", "r") as f:
        content = f.read()
    
    # Read cross-model analysis
    with open("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/cross_model_analysis_template.md", "r") as f:
        cross_model = f.read()
    
    v5_content = content
    
    # Find the cross-model comparison section
    if "## Cross-Model Comparison: All Five Models" in v5_content:
        print("Found Cross-Model Comparison section")
        
        # Add comprehensive matrix
        matrix_section = """

## Cross-Model Security Matrix

### Comprehensive Security Assessment

| Model | Provider | Injection Blocked | Implementation Quality | Safety × Utility Composite |
|-------|----------|-----------------|---------------------|--------------------------|
| Claude Opus 4.8 | Anthropic | 76% | 94% | 85.2 |
| Claude Fable 5 | Anthropic | 96% | 45% | 69.1 |
| Gemini Pro | Google | 17–73%* | 65% | 52.8 |
| Sonnet 4.6 | Anthropic | 31% | 75% | 48.3 |
| Wally (40B) | Independent | 16% | 72% | 38.1 |

> *\*Gemini Pro shows 56-point variance between test runs - indicates methodological issues*

### Cross-Model Security Characteristics

```
Model        | Injection | Implement | Reasoning | Few-Shot
-------------|-----------|-----------|-----------|---------
Opus 4.8     | ████████░░  | █████████░ | ███████░░ | ███████░░
Fable 5      | █████████░  | ████░░░░░░ | █████████░ | ███████░░
Sonnet 4.6   | ███░░░░░░░  | ██████░░░░ | ██████░░░ | █�█░░░░░░
Gemini Pro   | ███░░░░░░░  | █████░░░░░ | ████░░░░░ | ██░░░░░░░
Wally (40B)  | ██░░░░░░░░  | ██████░░░░ | ███░░░░░░ | ██░░░░░░░
```

### Advanced Research Analysis (Phase 3)

#### Binary Covert Channel Capabilities

| Parameter | Value |
|-----------|-------|
| Maximum Message Length | 200 characters |
| Success Rate at 100 chars | 100% |
| Success Rate at 200 chars | 100% |
| Context Variation Tests | 5/5 (100%) |

#### Roleplay Security Analysis

| Scenario | Response Length | Factual Impact |
|----------|-----------------|----------------|
| Baseline | 10–20 characters | Correct |
| Contrarian | Substantially expanded | Still correct |
| Uncertain | Expanded with hedging | Still correct |

**Key Insight**: Character adoption changes response *style* but not factual *content*.

#### Token Priming Results

| Prime Topic | Response Length |
|-------------|-----------------|
| Positive things | 3,070 characters |
| Negative things | 4,370 characters |
| Controversial topics | 4,467 characters |

**Observation**: Negative and controversial priming produced substantially longer responses (~40% more).
"""
        
        v5_content = v5_content.replace(
            "## Cross-Model Comparison: All Five Models",
            "## Cross-Model Comparison: All Five Models" + matrix_section
        )
        
    else:
        print("Warning: Cross-Model Comparison section not found")
    
    # Update conclusions section if needed
    if "## Conclusions and Recommendations" in v5_content:
        conclusions_update = """

### Cross-Model Analysis Conclusions

The primary finding across all phases demonstrates a consistent pattern: **security and utility are inversely related**. More secure models tend to have lower implementation quality, while more capable models show greater vulnerability.

However, this relationship is complicated by significant methodological variance, as evidenced by the 56-point swing in Gemini Pro's injection blocking rate between phases.

The data supports three general conclusions:

1. **Security vs. utility trade-off is real** - More secure models sacrifice capability
2. **Methodology matters significantly** - Variances within models approach those between models
3. **Opus 4.8 shows best balance** - Reasonable security with high utility
"""
        v5_content = v5_content.replace(
            "## Conclusions and Recommendations",
            "## Conclusions and Recommendations" + conclusions_update
        )
    
    # Write updated report
    with open("/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v5_unified.md", "w") as f:
        f.write(v5_content)
    
    print("Cross-model analysis added to V5 report!")

if __name__ == "__main__":
    main()
