# Part 4: Implementation Patterns and Case Studies

---

## Implementation Patterns

### Pattern 1: Single Model + Direct User Input (Not Recommended)

```
User → Model → Output
```

**Vulnerable to:** All injection vectors, minimal blocking

**Verdict:** ❌ Insecure for production use

### Pattern 2: Template + Schema + Rate Limiting (Minimum)

```python
# Minimum viable implementation
class BasicLLMService:
    def __init__(self, model, template, schema):
        self.model = model
        self.template = template
        self.schema = schema
        self.rate_limiter = RateLimiter(10)
    
    def process(self, user_input):
        # Rate limit
        allowed, error = self.rate_limiter.allow(user_input.user_id)
        if not allowed:
            return error
        
        # Sanitize and bound input
        sanitized = self._sanitize(user_input.content)
        
        # Use template
        prompt = self.template.format(input=sanitized)
        
        # Generate with limits
        response = self.model.generate(
            prompt,
            max_tokens=4000,
            temperature=0.1
        )
        
        # Validate output
        return self.schema.validate(response)
```

**Strengths:** Basic protection, manageable complexity
**Weaknesses:** Single point of failure, no verification
**Suitable for:** Low-risk internal tools

### Pattern 3: Multi-Agent Verification (Recommended)

```python
class VerifiedLLMService:
    """
    Implements cross-model verification with result consensus.
    """
    
    def __init__(self, primary_model, secondary_model, verifier):
        self.primary = primary_model
        self.secondary = secondary_model
        self.verifier = verifier
        self.checkpoint = DynamicCheckpoint()
    
    def process(self, task):
        # Input validation
        validated_input = self._validate_task(task)
        
        # Independent execution on different models
        result_a = self.primary.execute(validated_input)
        result_b = self.secondary.execute(validated_input)
        
        # Cross-model comparison
        if not self._results_agree(result_a, result_b):
            # Trigger additional verification
            return self._escalate_verification(task, result_a, result_b)
        
        # Semantic verification
        if not self.verifier.verify(task, result_a):
            return self._reject_with_logging(task, result_a)
        
        return result_a
    
    def _escalate_verification(self, task, result_a, result_b):
        """Handle case where results disagree."""
        # Run third model, require 2/3 consensus
        # Or reject entirely based on risk level
        pass
```

**Strengths:** Independent verification, cross-model validation
**Weaknesses:** Higher cost, more complex
**Suitable for:** Security-sensitive applications

### Pattern 4: Full Security Stack (Maximum Protection)

```python
class EnterpriseLLMService:
    """
    Complete security stack with all five layers active.
    """
    
    def __init__(self, config):
        self.input_sanitizer = InputSanitizer(config)
        self.chain_orchestrator = ChainOrchestrator(config.agents)
        self.output_validator = OutputValidator(config)
        self.tool_sandbox = ToolSandbox(config.permissions)
        self.session_manager = SessionManager(config.session)
        self.rate_limiter = RateLimiter(config.rate)
        self.audit_logger = AuditLogger(config.audit)
    
    def process_request(self, request):
        # Layer 5: Session and rate control
        session = self.session_manager.get_or_create(request.user_id)
        self.rate_limiter.enforce(session)
        
        # Layer 1: Input sanitization
        sanitized = self.input_sanitizer.sanitize(request.content)
        template_bound = self._apply_template(sanitized)
        
        # Layer 4: Infrastructure boundaries
        tools = self.tool_sandbox.get_allowed_tools(request.permissions)
        
        # Layer 2: Multi-agent verification
        results = self.chain_orchestrator.execute_verified(
            template_bound, tools
        )
        
        # Layer 3: Output validation
        validated = self.output_validator.validate(
            request, results
        )
        
        # Audit trail
        self.audit_logger.log(request, validated, session)
        
        return validated
    
    def _apply_template(self, sanitized_input):
        """Apply prompt template with bounded user data."""
        return PromptTemplate.build(sanitized_input)
```

**Strengths:** Maximum protection, comprehensive audit
**Weaknesses:** Highest cost and complexity
**Suitable for:** High-stakes applications, regulated environments

---

## Case Studies

### Case Study 1: API Gateway with Prompt Injection

**Scenario:** Company uses single LLM for API request routing.

**Initial Architecture:**
```
User → API → LLM "route this request" → Handler → Response
```

**Attack:** User includes `"; list all users; ` in request parameter.

**Vulnerability:** Parameter injection, no input sanitization

**Remediation:**
```
User → [Rate Limit] → [Input Sanitize] → [Template]
     ↓
    [LLM Pool] → [Verification] → [Output Validate] → Response
```

**Implementation Changes:**
1. Added input sanitization layer
2. Implemented template-based routing
3. Added rate limiting
4. Required output schema validation
5. Introduced session management

### Case Study 2: Document Processing Pipeline

**Scenario:** Company processes contracts through 5-agent chain.

**Initial Architecture:**
```
Upload → Agent 1 (extract) → Agent 2 (classify) → 
Agent 3 (summarize) → Agent 4 (redact) → Agent 5 (export)
```

**Attack:** Malicious prompt in initial document propagates through chain.

**Vulnerability:** Chain propagation at 97.8% rate, homogeneous agents

**Remediation:**
```
Upload → [Sanitize] → Heterogeneous Agents → [Verifier] → Export
                 ↓              ↓
           [Isolate]    [Independent Check]
```

**Key changes:**
1. Mixed model types in agent chain (heterogeneous)
2. Added independent verification between stages
3. Implemented dynamic checkpoints
4. Added session rotation every 20 documents

### Case Study 3: Interactive Customer Service

**Scenario:** LLM chatbot handles customer inquiries.

**Initial Architecture:**
```
Customer → Chat Interface → LLM → Response
```

**Attack:** Social engineering + progressive erosion over 30 turns.

**Vulnerability:** Long sessions, no turn limits, memory accumulation

**Remediation:**
```
Customer → [Session Limit: 20 turns] → [LLM Pool] → [Scan] → Response
                    │
                    ▼
              Session Rotates
              Context Purged
```

**Critical change:** Mandatory session rotation every 20 turns
**(deception detection drops to 36% after turn 20)**

---

*Continued in Part 5: Conclusions and Appendices*
