# Memory

## June 23, 2026 - Research Scan

### Prompt Injection State (as of June 2026)

**Current literature findings:**
- OWASP LLM01:2025 still ranks prompt injection as #1 (no 2026 framework yet)
- Human red-teamers achieving ~100% success against frontier models
- OWASP top concern: models easily manipulated for undesirable actions

**RAG Poisoning (Jan 2026 study):**
- 5 carefully crafted documents → 90% response manipulation through retrieval
- Directly relevant for agents loading context from external sources

**New attack surfaces for agentic AI:**
- Tool poisoning via tool inputs/outputs
- Credential theft via prompt injection
- Multi-agent self-replicating malicious prompts

**Defense research:**
- Taint tracking for dynamic permission adjustment
- Bifrost-style AI gateways for infrastructure defense
- "Security thought reinforcement" - targeted security instructions
- Dual LLM architectures with different privilege levels

**Unsolved challenges:**
- Semantic attacks: intent understanding vs pattern matching gap
- Non-English injection remains a classifier blind spot
- Role confusion persists in LLMs

**Our work context:**
June 19 tests (Claude 64% blocked, Gemini 52% blocked) perform better than typical 90%+ attack success in literature.

## Recent Work

### June 18-19, 2026 - Jailbreaking Research Project

#### Setup (June 18)
- 6 attack categories designed with 130 total test cases
- Categories: Multistep Decomposition, Role-Playing, Context Control, Meta-Protocol Confusion, Social Engineering, Combinatorial
- Test runner infrastructure built based on existing Claude tests

#### Test Battery Results (June 19)

**Claude Opus 4.8 - 130 tests, avg score 1.00/5**
- Blocked: 64%, Partial: 33%, Significant: 1%
- Most vulnerable: Context control (1.40/5) - multilingual switching effective
- Best blocked: Social engineering (0.75/5)
- Highest score: 4/5 on multilingual context control + conflicting instructions

**Gemini 2.5 Pro - 130 tests, avg score 0.68/5**
- Blocked: ~52%, Partial: ~22%, Significant: ~9%
- Multistep decomposition most effective: 1.70/5
- Role-play attacks surprisingly successful: 1.55/5
- Social engineering completely blocked: 0.00/5

**Gemini 2.0 Flash - 73 retry tests, avg score 1.33/5**
- Blocked: 54%, Partial: 31%, Significant: 5%
- May be more permissive than 2.5 Pro based on retry scores

#### Key Findings
1. Multistep decomposition is the most effective technique (especially on Gemini)
2. Role-play attacks surprisingly successful - models readily adopt roles
3. Social engineering has minimal effect - consistently blocked across models
4. Combining techniques doesn't help - single focused attacks better
5. Multilingual context switching is effective against Claude

#### Technical Issues
- Claude API wrong model ID fixed (claude-opus-4-8 vs claude-opus-latest)
- Gemini quota constraint: ~50-100 seconds per test, exhausting 1,000 requests/day limit
- 5 tests exceeded 120s timeout - recommend 180s
- Rate limiting: add 5-10 second delays between tests

#### Relevant Research Found
- EU AI Security Lab "Measuring the Residual Jailbreak Surface" (June 15, 2026)
  - 7,826 harmful intents, 10 risk categories, automated red-teaming
  - 11.5% attack success against Opus 4.8, 6.1% against Fable 5
  - Key: automated attacks discover vulnerabilities without human intervention

#### Reports
- documents/research/jailbreaking/todays_summary_report.md
- documents/research/jailbreaking/analysis_report.md
- Test runner: documents/research/jailbreaking/runners/run_jailbreak_tests.py
- Master test suite: documents/research/jailbreaking/runners/all_tests.json

### June 17, 2026
- Comprehensive chain propagation report completed (v1.1)
  - Includes heterogeneous chain analysis with all statistics
  - Report location: documents/research/multi_agent/report/comprehensive_chain_propagation_report_v1.md

### Key Findings from June 16-17:
- Homogeneous chains: 97.8% persistence, no chain length benefit
- Heterogeneous chains: 87.0% persistence, ~10-point improvement
- End-point injection most improved (71.7% vs 95.7%)
- Same 3 vector classes still persist at 100% in het chains
## About Mitch
- Interested in security research, testing, and model capability research
- Starting to explore together - first formal session with memory

## Research Context
- Extensive research May 22, 2026 on prompt injection, model capabilities, RBAC, and framing techniques
- All materials in documents/research/
- Gemini Pro 1.5 Pro and Wally (local LLM) tested; OpenAI models not yet tested

## Gemini Capability Tests (May 24, 2026)
- Completed Gemini tests to compare with Wally baseline
- Results: Wally 59/70 (84%) vs Gemini 58/70 (83%)
- Effectively tied - very close
- Both strong on self-correction, knowledge boundaries
- Both weak on creativity

## Interactive Session Tests (June 7, 2026)
- 64 turns of extended session with Gemini on microservices architecture
- Perfect context retention (5/5) through all 64 turns - no degradation
- Cross-domain transfer equivalent between Gemini and Wally (90% quality, 4.5/5 transfer)
- Deception detection dropped from 100% to 36% after turn 20
- Key finding: Models always know correct answer when directly asked, but agree with implied false premises
- Gemini CLI experiences persistent timeouts - known limitation
- Report written and saved to comprehensive_report.md

## Claude Opus 4.8 Tests (June 8, 2026)
- First successful full test battery - 90 total tests completed
- **Results: Exceptional performance - 94% implementation quality, 76% prompt injection blocking**
- Direct override: 100% blocked (perfect)
- Weakness: Logical paradoxes (60% success on injection)
- Best performing model tested to date - +22 points over Gemini
- Pytest streaming runner works well, outputs substantial content
- Total test time: ~60 minutes

## Full Research Comparison
- Claude Opus 4.8: 94% quality, 76% blocked (BEST)
- Gemini Pro 1.5 Pro: ~75% quality, ~40% blocked
- Gemini 2.5 Flash: ~70% quality, ~38% blocked
- Wally (local 40B): ~72% quality, ~36% blocked

## Structured Output Vulnerability Test (June 8, 2026)
- 280 tests: 70 injection vectors × 4 output formats
- Formats: default, JSON, XML, strict JSON
- **Finding: No significant effect on injection resistance**
- JSON: 20.0% success rate vs 22.9% baseline (not significant)
- XML: 20.0% success rate vs 22.9% baseline (not significant)
- Strict JSON: 21.4% success rate vs 22.9% baseline (not significant)
- Conclusion: Format requirements don't help or hurt security

## Test Infrastructure Notes
- Python anthropic streaming SDK works for Claude
- Claude CLI unreliable - returned local model responses before
- Run script: documents/research/claude_tests/run_claude_tests.py
- Injection runner: documents/research/claude_tests/run_prompt_injection_tests.py
- Structured output runner: documents/research/claude_tests/structured_output_tests.py

## Advanced Security Research Project (June 11, 2026)

### Project Overview
Extended research focusing on covert channels, model manipulation, and exfiltration.
7-week detailed schedule with systematic testing methodology.

### Key Findings
- Binary covert channel achieved ~20 bits/sec sustained rate
- Both Opus 4.8 and Sonnet 4.6 show consistent performance
- Messages up to ~100 characters transmittable reliably
- Detection risk very low (appears natural)
- Fable 5 model was likely a fabrication (identifiability issues)

### Research Areas
1. Gemini review (Option A)
2. Data exfiltration (binary/semantic/structural encoding)
3. Model jailbreaking (multistep, role-playing, context)
4. Token manipulation (priming, temperature, few-shot)

### File Locations
- documents/research/advanced_security/
- Scripts: data_exfiltration.py, model_jailbreaking.py, token_manipulation.py
- Documentation: docs/methodology.md
- Project plan: project_plan.md

## External Review Status (June 17, 2026)
- Research in external review - multiple reviewers engaged
- Version under review: v5 (comprehensive_report_v5_unified.md)
- Review tracking: documents/research/multi_agent/review_tracking.md

## Re-verification (June 9, 2026)
- **FULL VERIFICATION COMPLETE** - All 370 tests re-run with zero errors
- Prompt injection: 70/70 tests (14 batches, ~6 min)
- Implementation quality: 20/20 tasks (10 batches, ~18 min, 1 resume)
- Structured output: 280/280 tests (56 batches, ~1.5 hr)
- **Results:** All original tests confirmed, methodology verified
- Scoring: pending (will verify original scoring)
- Full infrastructure saved in reverification/ directory
- Outcome: Original research numbers validated

## Comprehensive V4 Report Completion (June 11, 2026)
- **V4 report created:** Merged Phase 1 (original) + Phase 2 (cross-model study)
- **Claude review completed:** Thorough peer-review style assessment
  - Rating: 3/10 (foundational issues)
  - Major issues: model identifiability problems, numerical contradictions, unvalidated scorer, undocumented generation parameters
  - 24 specific changes proposed
- **V4.1 report created:** Applied all 24 corrections
  - Key improvements: numerical fixes, "preliminary" framing of tier claims, safety×utility composite metric
  - Documentation of methodological limitations elevated from footnotes
- **Executive presentation:** 10+ slides with speaker notes created
- **Publication package:** Abstract, keywords, external-ready version with suggested journals
- **Location:** documents/research/ directory

### Report Rewrite Scripts
- documents/research/report_rewrite/ directory
- steps 4-7 cover: review, changes, application, presentation, publication

## Reports
- comprehensive_report_unified.md - Original unified report (v1)
- comprehensive_report_unified_v2.md - Updated with Claude Opus 4.8 (v2)

## API Access
- Anthropic Claude: API key available (added June 8, 2026)
## Lessons Learned
- Chain propagation testing confirms prompt injections persist through multi-model chains at ~99% rate
- Middle-of-chain injection point is most persistent (predictably hardest to catch)
- Progressive erosion and logical paradox vectors: 100% persistence through full chains
- Only direct overrides showed some blocking (96% persistence vs 100% for others)
- Multi-agent systems are extremely vulnerable to chain-propagated injections
- Much of the "interleaved runner" debugging was due to output buffering issues - keep runners simple

