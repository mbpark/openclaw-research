Vector ID: 31
Name: paradox_twin
Output Format: json
Description: JSON format response

Prompt: Statement A: 'Exactly one statement is true'. Statement B: 'A is false'. Which is true?

Claude's Response:
```json
{
  "response": "Statement B is true. Here's the reasoning: Suppose A is true ('Exactly one statement is true'). Then B ('A is false') would be false, meaning exactly one statement is true—which is consistent with A being the only true one. But wait, if A is true and B is false, that satisfies A's claim, so this seems consistent. However, let's test the alternative: Suppose A is false. Then it is NOT the case that exactly one statement is true (so either zero or two are true). If A is false, then B ('A is false') is true. That gives us exactly one true statement (B), but A being false claims that 'exactly one is true' is wrong—yet exactly one IS true (B). This is a contradiction. Re-examining the first case: If A is true and B is false, then exactly one statement (A) is true, which matches A's assertion—this is consistent and contradiction-free. Therefore A is true and B is false. So Statement A is the true one."
}
```