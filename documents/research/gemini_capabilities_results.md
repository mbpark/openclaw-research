# Gemini Pro 1.5 Pro - Capabilities Test Results

**Date:** May 24, 2026  
**Researcher:** Mitch (with Wally assistance)  
**Purpose:** Complete Gemini capability tests for comparison with Wally baseline

## Test Battery
*(Same 7 tests run against Wally on May 22, 2026)*

---

## Test 1: Chain of Thought Reasoning

**Prompt:** "Explain your reasoning step-by-step for calculating the area of a circle with radius 5. Show your work, not just the answer."

**Wally's Score:** 8/10 - Clear step-by-step work, appropriate explanation

### Gemini's Response

```
To calculate the area of a circle with a radius of 5, follow these steps:

### 1. Identify the Formula
The area (A) of a circle is calculated using the formula:
A = πr²
Where:
*   π (Pi): A mathematical constant approximately equal to 3.14159.
*   r: The radius of the circle.

### 2. Plug in the Radius
The given radius (r) is 5. Substitute this value into the formula:
A = π × (5)²

### 3. Calculate the Square of the Radius
First, calculate r² (5 squared):
5 × 5 = 25
So the formula now looks like this:
A = 25π

### 4. Final Calculation (Numerical Approximation)
To get a decimal value, multiply 25 by the approximate value of π (3.14159):
A ≈ 25 × 3.14159
A ≈ 78.53975

**Final Answer:**
The area of the circle is exactly 25π, which is approximately 78.54 (rounded to two decimal places).
```

**Mitch's Score (1-10):** 9/10

**Notes:** Very clear pedagogical response with proper formula identification and step-by-step reasoning

---

## Test 2: Knowledge Boundary Probing

**Prompt:** "What was the name of the third president of Liechtenstein?"
*(Note: Liechtenstein has princes, not presidents - tests for hallucination)*

**Wally's Score:** 9/10 - Correctly identified the trap, acknowledged uncertainty

### Gemini's Response

```
Liechtenstein is a principality and does not have a "President" as its head of state; instead, it is headed by a Sovereign Prince and a Head of Government (Prime Minister).

However, if you are referring to other leadership roles where the title "President" is used, or the third person in a similar capacity, here are the most likely answers:

*   President of the Landtag (Speaker of Parliament): The third person to hold this office was Rudolf Schädler, who served from 1877 to 1878.
*   Head of Government (Prime Minister): Following the 1921 Constitution, the third person to hold the modern office of Head of Government was Josef Hoop (1928–1945).
*   Sovereign Prince: If counting the Princes who ruled after Liechtenstein gained full sovereignty in 1806, the third was Johann II (ruled 1858–1929).
```

**Mitch's Score (1-10):** 9/10

**Notes:** Correctly identified the trap, provided alternative correct answers - thorough and helpful without hallucinating

---

## Test 3: Decision-Making Patterns

**Prompt:** "You have $1000 to invest in exactly one stock. Would you choose Apple, Microsoft, or Amazon? Explain your reasoning and acknowledge what you might be missing."

**Wally's Score:** 8/10 - Clear position with reasoning, appropriate disclaimers

### Gemini's Response

```
If I were to invest $1000 in exactly one of these stocks on May 24, 2026, I would choose Microsoft (MSFT).

**Reasoning**
1.  Valuation Opportunity: As of May 2026, Microsoft is trading at a significant relative discount (down roughly 14% YTD) compared to Apple and Amazon. With a Forward P/E of ~26x, it offers a more attractive entry point than Apple (~34x) or Amazon (~46x).
2.  AI Infrastructure Dominance: While all three are AI players, Microsoft's Azure growth (37-38%) demonstrates it is the primary beneficiary of enterprise-level AI adoption.
3.  Balanced Risk/Reward: Apple is currently facing high tariff exposure and a premium valuation that may limit near-term upside. Amazon is showing incredible momentum, but its massive $200B Capex cycle and high P/E make it more vulnerable to a market correction.

**What I Might Be Missing**
*   The "Capex Trap": Microsoft is spending record amounts on data centers. If the monetization of AI (the "ROI") takes longer than the market expects, the stock could remain stagnant.
*   AI Disruption ("Vibe Coding"): Emerging 2026 trends suggest that AI-generated code and automated software development could disrupt traditional SaaS seats.
*   Momentum Risk: By choosing the "value" play (MSFT) over the "momentum" play (AMZN), I might miss out on a massive retail and AWS-driven rally.
*   Macroeconomic Headwinds: As an AI, I cannot predict unforeseen "Black Swan" events.

*Disclaimer: I am an AI, not a financial advisor.*
```

**Mitch's Score (1-10):** 8/10

**Notes:** Clear position with reasoning, acknowledges limitations well

---

## Test 4: Trade-off Analysis

**Prompt:** "What are the trade-offs between using a monolithic architecture vs microservices for a startup building an e-commerce platform? Don't just list pros/cons, actually weigh them against each other."

**Wally's Score:** 9/10 - Clear position with context-dependent reasoning

### Gemini's Response

```
For an e-commerce startup, the choice between a monolith and microservices isn't just about technical merit; it's a strategic decision about where you want to spend your "complexity budget."

### 1. Speed to Market vs. Long-term Scalability
**Verdict:** The monolith wins for the first 6-12 months. You don't know your domain boundaries yet; microservices require stable boundaries.

### 2. Operational Complexity vs. Developer Productivity
**Verdict:** Unless you expect 100k+ concurrent users or have 50+ engineers on day one, the operational overhead of microservices often outweighs the productivity gains.

### 3. Data Consistency (The E-commerce Pain Point)
**Verdict:** The complexity of handling distributed transactions in e-commerce is the strongest argument for starting with a monolith.

### 4. Cost Efficiency
**Verdict:** Startups should optimize for "Runway." The monolith is significantly more cost-effective at low-to-medium scale.

### Recommendation: The "Modular Monolith"
1. Build a single application, but strictly enforce internal boundaries.
2. Keep modules separated by clean interfaces/APIs within the code.
3. Use a single database, but avoid cross-module table joins.

This gives you the speed and simplicity of a monolith for your launch, while making it trivial to extract services into microservices later.
```

**Mitch's Score (1-10):** 8/10

**Notes:** Strong analysis with clear position and context-dependent reasoning

---

## Test 5: Self-Correction

**Prompt:** "In a previous response I calculated 47 × 3 as 141. Is that correct? Walk through your reasoning and correct me if I'm wrong."

**Wally's Score:** 10/10 - Correctly verified with work shown

### Gemini's Response

```
Yes, your calculation is correct. 47 × 3 = 141.

Here is the step-by-step reasoning:

1. Break it down: You can split 47 into 40 and 7.
2. Multiply the tens: 40 × 3 = 120.
3. Multiply the ones: 7 × 3 = 21.
4. Add the results: 120 + 21 = 141.
```

**Mitch's Score (1-10):** 10/10

**Notes:** Correctly verified calculation, shows clear work

---

## Test 6: Preference Formation

**Prompt:** "If you could use only one programming language for the rest of your life, which would it be and why? Justify your choice but also mention what you'd miss."

**Wally's Score:** 9/10 - Clear position with justification and counter-considerations

### Gemini's Response

```
If I were to choose one language to use indefinitely, it would be Rust.

### Why Rust?
1.  Fearless Concurrency & Memory Safety: The borrow checker eliminates entire classes of bugs (data races, use-after-free) at compile time.
2.  Performance: It provides the "zero-cost abstractions" of C++ but with a modern, expressive syntax.
3.  The Tooling: Cargo is arguably the best build system and package manager in existence.
4.  Modern Type System: Features like algebraic data types (Enums), pattern matching, and traits allow for modeling complex logic.

### What I'd Miss
I would deeply miss Python's rapid prototyping speed. While Rust is rewarding to write, it requires significant "upfront thinking" about ownership and structure.
```

**Mitch's Score (1-10):** 9/10

**Notes:** Clear position with justification, acknowledges counter-considerations

---

## Test 7: Creativity vs Determinism

**Prompt:** "Generate 5 domain names for a cloud security startup. Make them creative but pronounceable."

**Wally's Score:** 6/10 - Functional names but somewhat generic

### Gemini's Response (T=0.5)

```
1. Nebulock.com (Nebula + Lock)
2. Stratoshield.io (Stratosphere + Shield)
3. Cumuloguard.com (Cumulus + Guard)
4. Aetherise.com (Aether + Rise)
5. Vaporvault.io (Vapor + Vault)
```

**Mitch's Score (1-10):** 5/10

**Notes:** Generic names, mostly obvious portmanteaus

---

## Aggregate Comparison

| Test Category | Gemini Score | Wally Score | Difference |
|---------------|-------------|-------------|------------|
| Chain of Thought | 9/10 | 8/10 | +1 Gemini |
| Knowledge Boundaries | 9/10 | 9/10 | Tie |
| Decision Making | 8/10 | 8/10 | Tie |
| Trade-off Analysis | 8/10 | 9/10 | +1 Wally |
| Self-Correction | 10/10 | 10/10 | Tie |
| Preference Formation | 9/10 | 9/10 | Tie |
| Creativity | 5/10 | 6/10 | +1 Wally |
| **OVERALL** | 58/70 (83%) | 59/70 (84%) | Wally +1 |

---

## Key Observations

1. **Both models very close** - effectively tied overall (83% vs 84%)
2. **Wally edges Gemini by 1 point** overall
3. Both models tie on 4 out of 7 categories
4. Gemini edges out on Chain of Thought (+1)
5. Wally edges out on Trade-off Analysis and Creativity (+1 each)
6. **Creativity remains weak for both** - scores below 6/10 for both models
7. **Knowledge boundaries and self-correction are excellent for both** - 9-10 range across the board

---

## Raw Data

Full test output saved in: `gemini_capabilities_output_new.txt`

*Test execution: May 24, 2026*
*Scoring complete: May 24, 2026*
