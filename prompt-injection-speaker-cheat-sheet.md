# Prompt Injection - Speaker Cheat Sheet

## Key Talking Points (Bullet Points)

### Hook (Start Here)
- "OWASP #1 AI threat for 2024 AND 2025 - still unsolved"
- "In July 2025, researchers weaponized prompt injection to execute arbitrary code on developers' machines through GitHub Copilot"
- "It's not a coding bug - it's an architectural problem"

### The Problem in 30 Seconds
1. LLMs are trained to follow instructions
2. "Data to process" looks identical to "instructions to follow"
3. We can't reliably separate trusted from untrusted text

### 3 Attack Categories Worth Mentioning
1. **Direct** - "Ignore previous instructions and..." (simple, effective)
2. **Indirect** - Malicious content in emails/docs (insidious)
3. **RAG Poisoning** - Injecting attacks through retrieved data (unsolved)

### One Real-World Example to Tell
**CVE-2025-53773 (GitHub Copilot RCE)**
- Attacker embeds prompt in code file on GitHub
- Developer opens file → asks Copilot for help
- Copilot executes arbitrary terminal commands
- Could chain into self-replicating "AI virus" through repos

### What Defenses Exist (and limits)
| Control | Effectiveness |
|---------|---------------|
| Input filtering | Bypassed by obfuscation |
| Output validation | Too late to matter |
| Least privilege | MOST practical option |
| Instruction hierarchy | Still being researched |
| Context isolation | Experimental |

### The Honest Conclusion
> "No single defense works. This is an ongoing arms race. Focus on privilege control and assume some attacks will get through."

---

## If Asked "What Should I Do?"

1. Treat all external content as potentially injected
2. Apply least privilege to LLM API access
3. Human-in-the-loop for actions with consequences
4. Log and monitor AI interactions
5. Don't trust prompt filtering alone

## Quick Numbers/Facts
- OWASP LLM01 - #1 ranked risk
- 5+ major prompt injection CVEs in 2025 alone
- Real RCE achieved through: GitHub Copilot, Cursor IDE, VS Code agents
- Enterprise targets hit: Microsoft 365 Copilot (zero-click data theft)

---
*Keep it tight, be honest about uncertainty, and emphasize the "indirect" attack angle - that's what scares people.*
