 # Prompt Injection: Executive One-Pager

> *"The attacks are happening. The data is leaking. Most companies have no idea."*

---

## THE PROBLEM IN 30 SECONDS

AI systems can't distinguish between **instructions** and **data**. Attackers embed instructions inside data, and the AI obeys — leaking data, executing actions, bypassing security.

Think SQL injection, but for your brain.

---

## FOUR REAL INCIDENTS

| Incident | What Happened | Financial Impact |
|----------|---------------|------------------|
| **EchoLeak (CVE-2025-32711)** | Zero-click email leaked Microsoft 365 Copilot data | CVSS 9.3 / critical |
| **Fortune 500 Bank (Mar 2025)** | Customer extracted account data via AI chatbot for 7 months | $65M+ in fines |
| **Otter.ai (2026)** | Meeting summaries completely fabricated mid-meeting | Business decisions based on lies |
| **PromptLock (2025)** | Ransomware that uses AI itself to encrypt files | "Different malware every time" |

---

## THE STATISTICS

| Metric | Figure |
|--------|--------|
| **$4.4+ billion** | 2025 global AI security breach costs |
| **#1 AI threat** | OWASP LLM risk ranking (top of 10) |
| **42%** | AI security incidents involve prompt attacks |
| **Only 38%** | Companies have *any* defense in place |

---

## WHY THIS IS DIFFERENT

- **No single technical fix exists** — requires architecture change
- **Traditional tools don't detect it** — it's text, not code
- **Attacks improve monthly** — industry is still defining the problem
- **Most security teams don't know about it** — blind spot in defenses

---

## WHAT YOU NEED TO DO

### Week 1-2
- Inventory all AI systems with data access
- Remove direct data access from AI agents
- Start logging AI input/output

### Month 1-3
- Pen test AI systems for injection
- Add human approval for AI actions
- Review insurance coverage for AI incidents

### Month 6-12
- Redesign architecture (human-in-the-loop)
- Implement defense-in-depth
- Continuous testing program

---

## THE BOTTOM LINE

> *"SQL injection attacks were known for 15 years before companies fixed them. We're at year 2 of prompt injection. The data is being stolen now.*
>
> *If it hits your company and the Board finds out 'you didn't know about this risk?'*
>
> *That will be your testimony at the regulatory hearing."*

---

*Sources: OWASP, Crowdstrike, Microsoft CVE, ESET, Stanford CRIS, Obsidian Security*
