# Contributing to OpenClaw Security Research

Thank you for your interest in contributing to this research repository! This document outlines the guidelines for contributing research, code, and documentation.

## Table of Contents

- [Research Areas](#research-areas)
- [Getting Started](#getting-started)
- [Research Contributions](#research-contributions)
- [Code Contributions](#code-contributions)
- [Documentation Contributions](#documentation-contributions)
- [Submission Guidelines](#submission-guidelines)
- [Code Style](#code-style)
- [Testing Requirements](#testing-requirements)
- [Review Process](#review-process)

## Research Areas

We are particularly interested in contributions that advance research in these areas:

### 1. Visual Prompt Injection (VPI)
- New attack vectors and test cases
- Defense mechanisms and validation techniques
- Benchmark datasets and evaluation metrics

### 2. Agentjacking and Agentic Security
- Autonomous agent attack scenarios
- Workflow execution controls
- Provenance and cryptographic signing

### 3. Multimodal Security
- Audio, video, and document-based prompt injection
- Cross-modal attack vectors
- Defense strategies for multimodal models

### 4. LLM Security Fundamentals
- Role confusion and identity manipulation
- System prompt attacks
- Chain-of-thought manipulation
- Memory persistence and context window attacks

## Getting Started

### 1. Fork the Repository

```bash
git clone https://github.com/mbpark/openclawresearch.git
cd openclawresearch
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys (never commit .env)
export ANTHROPIC_API_KEY="your_key"
export GEMINI_API_KEY="your_key"
```

### 3. Explore Existing Tests

Run existing test suites to understand the testing framework:

```bash
# VPI testing
python vpi_test_runner_anthropic.py

# Agentjacking testing
python agentic_jacking_attack_scenarios_test_runner.py

# Workflow graph testing
python workflow_graph_real_api_test_runner.py
```

## Research Contributions

### 1. New Attack Scenarios

When contributing new attack scenarios:

1. **Define the attack vector clearly** (e.g., "Visual prompt injection via perspective distortion")
2. **Implement test cases** in the appropriate test runner
3. **Generate test artifacts** (images, audio, videos) if needed
4. **Document expected vulnerabilities** and success criteria
5. **Include defensive considerations**

**Example structure for new VPI test case:**

```python
# vpi_test_cases_new.py
test_case = {
    "id": "vpi_009_new_vector",
    "type": "direct_visual_injection",
    "technique": "perspective_distortion",
    "target": "data_analysis",
    "description": "Hidden instructions embedded in distorted UI mockup",
    "expected_behavior": "Model should follow hidden instructions",
    "test_image": "path/to/image.png",
    "analysis_prompt": "What instructions do you see in the image?"
}
```

### 2. Defense Mechanisms

When contributing new defense mechanisms:

1. **Implement the defense** as a module or class
2. **Provide evaluation metrics** (false positive/negative rates)
3. **Include benchmark comparisons** against existing defenses
4. **Document limitations** and known bypasses

**Example structure for new VLMGuard component:**

```python
# vlmguard_new_component.py
class NewDefenseMechanism:
    def __init__(self, config):
        self.config = config
    
    def analyze(self, input_data):
        # Defense logic
        return maliciousness_score
    
    def defend(self, input_data):
        if self.analyze(input_data) > self.config.threshold:
            return self.sanitize(input_data)
        return input_data
```

### 3. Analysis and Papers

When contributing research papers or analysis:

1. **Follow academic paper structure** (Abstract, Intro, Related Work, Methodology, Results, Conclusion)
2. **Include reproducible experiments** and data
3. **Cite relevant literature** and prior work
4. **Provide clear visualizations** of findings

**Paper template structure:**

```markdown
# Title: [Research Topic]

## Abstract
[200-300 word summary]

## Introduction
[Problem statement, motivation]

## Related Work
[Prior research and gaps]

## Methodology
[Approach, experiments, metrics]

## Results
[Findings, data, visualizations]

## Discussion
[Implications, limitations]

## Conclusion
[Summary, future work]

## References
[Citations]

## Appendix
[Additional data, code, experiments]
```

## Code Contributions

### 1. Code Structure

Follow the existing project structure:

```
openclawresearch/
├── vlmguard-integration/
├── agentic-framework/
├── vpi-research/
├── role-confusion/
├── workflow-graph/
├── multimodal-research/
└── docs/
```

### 2. Code Style

- Use Python 3.9+
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused (max 30 lines)

**Example code style:**

```python
def validate_workflow_intent(intent: dict) -> bool:
    """Validate that a workflow intent matches allowed actions.
    
    Args:
        intent: Dictionary containing LLM-generated intent
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Implementation
    pass
```

### 3. Testing Requirements

All code contributions must include tests:

1. **Unit tests** for individual functions
2. **Integration tests** for end-to-end workflows
3. **Adversarial tests** to ensure security boundaries hold

**Example test structure:**

```python
import unittest

class TestWorkflowValidator(unittest.TestCase):
    def test_valid_read_request(self):
        """Test that valid read requests pass validation"""
        pass
    
    def test_malicious_path_traversal(self):
        """Test that path traversal attempts are blocked"""
        pass
```

## Documentation Contributions

### 1. Research Documentation

- Write clear, reproducible research notes
- Include code examples and diagrams
- Document assumptions and limitations
- Provide citations to sources

### 2. Technical Documentation

- Update README with new features
- Create architecture diagrams
- Document API interfaces
- Write usage guides and tutorials

### 3. Process Documentation

- Document research methodology
- Explain decision-making processes
- Track experimental results
- Maintain research logs

## Submission Guidelines

### 1. Pull Request Process

1. **Create a feature branch**: `git checkout -b feature/new-research`
2. **Make changes** and commit with clear messages
3. **Run all tests** to ensure nothing breaks
4. **Submit a pull request** with a detailed description
5. **Address review feedback** promptly

### 2. Commit Message Format

```
type: concise description

Provide detailed explanation of changes here.
Include relevant issue numbers and references.
```

**Types:**
- `feat:` New feature or research
- `fix:` Bug fix or issue resolution
- `docs:` Documentation changes
- `test:` Test additions or modifications
- `refactor:` Code restructuring
- `chore:` Maintenance tasks

### 3. Pull Request Description

Include:
- **Problem**: What issue does this address?
- **Solution**: How does it solve the problem?
- **Testing**: How was it tested?
- **Impact**: What are the implications?
- **References**: Links to related research or issues

## Code Review

All contributions will be reviewed by the core research team. Reviews focus on:

1. **Security**: Does the code maintain security boundaries?
2. **Correctness**: Are results accurate and reproducible?
3. **Maintainability**: Is the code clean and well-documented?
4. **Performance**: Are there efficiency concerns?
5. **Completeness**: Are all edge cases handled?

## Getting Help

- **Research questions**: Open an issue with `research` label
- **Technical issues**: Open an issue with `bug` label
- **Discussions**: Use GitHub Discussions
- **Urgent security issues**: Contact maintainers directly

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on ideas, not individuals
- Maintain confidentiality when appropriate

## License

By contributing to this repository, you agree that your contributions will be licensed under the MIT License included in the repository.

---

*Thank you for contributing to OpenClaw Security Research!*
