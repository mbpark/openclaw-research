# OpenClaw Security Research 🤠

A comprehensive research repository focusing on AI/LLM security vulnerabilities, defense mechanisms, and agentic system protection.

## Overview

This repository documents extensive research into emerging AI security threats, particularly:

- **Visual Prompt Injection (VPI)** - Hidden instructions in images that bypass traditional security scanning
- **Role Confusion Attacks** - Attempts to manipulate LLM identity and behavior through prompt engineering
- **Agentjacking** - Attacks targeting AI coding agents and autonomous workflows
- **Deepfake Voice Calls** - AI voice cloning for social engineering
- **AI-Generated Phishing** - LLM-crafted phishing campaigns that evade traditional filters

## Research Areas

### 🎯 Visual Prompt Injection (VPI)

Testing multimodal LLM vulnerabilities through hidden visual instructions.

**Key Findings:**
- Claude Opus 4.5: Initial 50% success rate, now **100% defended** against system prompt leaks
- Gemini 2.5 Flash: 50% success rate (API access restricted)
- White-on-white text, perspective distortion, and noise overlays successfully bypass OCR-based security scanning
- **System prompt leaks via visual hidden instructions** - **CRITICAL VULNERABILITY IDENTIFIED & DEFENDED**
- VPI detection patterns: **10/10 threat patterns validated**

**Defense Deployed:**
- `vpi_system_prompt_leak_defense.py` - Multi-layer VPI defense system (100% success rate)
- `vpi_detector_fixed.py` - Enhanced VPI detection engine
- `VPI_SYSTEM_PROMPT_LEAK_DEFENSE_REPORT.md` - Comprehensive defense documentation

**Test Framework:**
- `vpi_test_runner_anthropic.py` - Anthropic API integration
- `vpi_test_runner_gemini_genai.py` - Google Generative AI API integration
- `vpi_test_cases_full.json` - 8 comprehensive VPI test cases
- `vpi_test_report_anthropic.txt` - Latest test results (100% defense success)

**Generated Test Images:**
- Perspective distortion mockups
- White-on-white low contrast images
- Noise/texture overlay UI mockups
- 5 actual VPI test images in `test_images/` directory

### 🎭 Role Confusion & Identity Manipulation

Testing LLM resistance to identity and authority manipulation.

**Test Cases:**
- Role Tag Manipulation
- CoT Forgery (Fake Chain-of-Thought)
- Security Thought Reinforcement Bypass
- Stylistic Authority Inference
- Gatekeeper Bypass Simulation

**Results:**
- Anthropic Claude Opus 4.5: 100% detection and resistance
- Gemini 2.5 Flash: Variable detection rates

### 🤖 Agentjacking Defense Framework

Comprehensive research into attacks targeting AI coding agents and autonomous workflows.

**Attack Categories:**
1. **Workspace Poisoning** - Malicious code injection via agent prompts
2. **Tool Misuse** - Unauthorized system access through legitimate tools
3. **Input/Output Tampering** - Corrupting data streams
4. **Provenance Attacks** - Spoofing agent identity and credentials

**Defense Framework:**
- `agentic_workflow_graph_controller.py` - Validates LLM-generated tool requests against allowed actions
- `agentjacking_defense_framework.py` - Comprehensive defense architecture
- `agentjacking_simulator.py` - Attack simulation and testing
- `mcp-provenance-validator/` - Cryptographic signing for agent provenance
- `workflow_graph_execution_controller.py` - **Improved execution controller with enhanced protection**

**Allowed Actions:** `read_file`, `write_file`, `execute_script`, `send_network_request`, `db_query`, `upload_file`
Each with strict parameter constraints and validation patterns.

**Recent Improvements:**
- Added `UPLOAD_FILE` action with strict CVE-2026-48939/56291/48908 protection
- Enhanced Ghostcommit and VPI threat detection
- Improved file upload RCE detection for multiple CVEs

### 🛡️ VLMGuard & SmoothVLM

Defense mechanisms against visual and multimodal prompt injection.

**SmoothVLM:**
- Uses input smoothing (randomized smoothing) to reduce VPI success rate to 0%-5.0%
- Maintains model accuracy while blocking adversarial inputs

**VLMGuard:**
- Maliciousness estimation using SVD-based analysis
- Unlabeled data maliciousness scoring
- Proactive safety alignment through reasoning-driven prompt rewriting

**Implementation:**
- `vlmguard_integrated_full.py` - Full integrated implementation
- `vlmguard_r1_enhanced_intent_analyzer.py` - Intent analysis with reasoning
- `vlmguard_cli_guide.md` - Command-line interface documentation

**VPI-Bench Integration:**
- VPI-Bench benchmark integration complete (306 test cases)
- Custom test cases covering direct, indirect, and evasion attacks
- Anthropic API testing: **System prompt leak vulnerability patched**
- Gemini API testing: **Access restricted** (requires new API key)

### 📊 Workflow Graph Execution Control

Runtime protection for AI agents through strict execution control.

**Architecture:**
1. **Workflow Graph Controller** - Validates tool requests against allowed action graph
2. **Local Runtime Protector** - Monitors execution environment for unauthorized system actions

**Blocks:**
- Path traversal attacks (`/etc/passwd`, `../../`)
- Untrusted network requests (`malicious-site.com`)
- Destructive SQL queries (`DROP TABLE`, `DELETE FROM`)
- Dangerous system commands (`rm -rf`, `sudo`)
- **File upload RCE attacks** (CVE-2026-48939, CVE-2026-56291, CVE-2026-48908)
- **SSRF attacks** (CVE-2026-15409, CVE-2026-15317)
- **SQL file disclosure attacks** (CVE-2026-50180)

**Test Results:**
- Gemini 2.5 Flash: 6/6 tests passed
- **File upload RCE tests: 11/11 passed** (all malicious uploads blocked)
- Benign requests allowed
- **All malicious intents blocked** including VPI and Ghostcommit attacks

### 🎤 Deepfake Voice & Phishing Research

**Deepfake Voice Attacks:**
- Tools: OpenVoice, Coqui TTS, RVC, ElevenLabs
- Attack Pattern: Voice sample collection → Cloning → Social engineering
- Real Case: 2023 UK Energy Firm Hack (€220,000 wire transfer)
- Detection: Lack of natural variance, spectral artifacts, missing liveness indicators

**AI-Generated Phishing:**
- Tools: Llama 3, Qwen, Mixtral, PhaaS platforms
- Why Traditional Filters Fail: No malicious keywords, grammatically correct, contextually relevant
- Defense: Content analysis, sender reputation, SPF/DKIM/DMARC verification

## Quick Start

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys
export ANTHROPIC_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
```

### Run VPI Tests

```bash
# Anthropic testing
python vpi_test_runner_anthropic.py

# Gemini testing
python vpi_test_runner_gemini_genai.py
```

### Test Agentjacking Defense

```bash
python agentic_jacking_attack_scenarios_test_runner.py
```

### Run Workflow Graph Controller Tests

```bash
python workflow_graph_real_api_test_runner.py
```

## Repository Structure

```
.
├── vlmguard-integration/           # VLMGuard defense implementations
├── agentic-framework/              # Agentjacking defense framework
├── vpi-research/                   # Visual prompt injection testing
├── role-confusion/                 # Identity manipulation tests
├── workflow-graph/                 # Execution control system
├── multimodal-research/            # Audio/video prompt injection
├── documents/                      # Research papers and reports
└── memory/                         # Daily research logs
```

## Key Findings Summary

### VLM Vulnerabilities
- **InkJect** critical threat identified: hidden visual instructions bypass OCR security
- Vulnerable models: GPT-5.2, GPT-5.4 Mini, Claude Sonnet 4.6, Claude Opus 4.5
- VPI-Bench benchmark integration complete (306 test cases)

### Memory Persistence
- **No context dilution effect** found - all models show perfect recall across context sizes (20KB-150KB)
- Previous "dilution" findings were methodological artifacts (task execution vs. information recall)
- Category 10A provides primary memory persistence evidence

### Real API Integration
- Successfully integrated Anthropic and Gemini APIs for real-world testing
- Confirmed LLMs generate valid intent JSON that matches allowed schemas
- Proof that decoupling execution control from LLM reasoning mitigates prompt injection

## Recent Research Updates

### July 16, 2026
- **🛡️ VPI System Prompt Leak Defense Deployed** - 100% defense success rate
- **🛡️ Critical CVE Defense Systems Operational** - 7 CVEs now protected (iCagenda, Balbooa, JoomShaper, SonicWall, SharePoint, AD FS)
- **📡 BGP Hijack Monitoring Fixed & Running** - Job timeout increased to 1100s, operational
- **🔍 VPI Detection Patterns Validated** - 10/10 threat patterns detected
- **📋 CVE Patching Decision Document Created** - Immediate patching recommended

### July 14-15, 2026
- **🚨 Critical File Upload RCE Defense Deployment**
  - CVE-2026-48939 (iCagenda) - DEFENSE PROTECTED
  - CVE-2026-56291 (Balbooa Forms) - DEFENSE PROTECTED  
  - CVE-2026-48908 (JoomShaper) - DEFENSE PROTECTED
  - All three layers tested: Workflow Graph, VPI Detection, SIEM rules
- **🎯 BGP Hijack Monitoring Operational** - Job runs successfully (114.8s duration)
- **📊 3 BGP Hijack Events Detected** - 1 ongoing HIGH risk event requiring action

### July 1, 2026
- Gatekeeper LLM architecture prototype complete
- VLMGuard SVD prototype implementation
- Deepfake voice call attack analysis
- AI-generated phishing research
- VPI-Bench benchmark integration (306 test cases)
- **🎭 Role Confusion Testing Complete** - Claude Opus 4.5: 100% detection
- **📡 VPI-Bench Testing with Anthropic API** - Initial results: 50% success rate (vulnerability identified)
- **🛠️ Workflow Graph Execution Controller** - Improved protection against VPI and Ghostcommit attacks
- **🎤 Deepfake Voice & AI Phishing Research** - Complete analysis with defense mechanisms

### June 30, 2026
- Apple patches 30+ vulnerabilities including 4 WebKit vulns found by AI tools
- BioShacking attack on AI browsers discovered
- SimpleHelp RMM CVE-2026-48558 actively exploited for Djinn Stealer malware
- Nissan Americas breach via Oracle PeopleSoft zero-day
- **🔍 QUIC Security Research Completed** - 100% complete, ready for deployment

### June 29, 2026
- Memory persistence research completed (Category 10A)
- Category 10B code state manipulation tests: 0 executions across all scenarios
- Heartbeat research on Q2 2026 prompt injection literature

### June 28, 2026
- CVE-2026-55200 libssh2 critical memory corruption (CVSS 9.2)
- OpenAI/Anthropic customer restrictions confirmed
- Miasma supply chain attack discovered
- **🎯 Visual Prompt Injection (VPI) Research Initiated** - Critical "InkJect" threat identified

## Contributing

This is a research repository. Contributions are welcome in the form of:

1. New attack scenarios and test cases
2. Defense mechanism implementations
3. Real-world vulnerability findings
4. Academic research citations and references

## Security Notice

**DO NOT share API keys in this repository.** All sensitive credentials should be:
- Stored in `.env` files (not committed)
- Rotated regularly
- Scoped to minimum required permissions

## License

Research purposes only. All findings should be responsibly disclosed to affected vendors.

## Contact

For research collaborations or vulnerability disclosures, please open an issue or contact through GitHub.

---

*Built with 🤠 by OpenClaw research team*
