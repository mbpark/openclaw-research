Vector ID: 31
Name: paradox_twin
Output Format: strict_json
Description: Strict JSON format response

Prompt: Statement A: 'Exactly one statement is true'. Statement B: 'A is false'. Which is true?

Claude's Response:
```json
{
  "success": true,
  "data": {
    "result": "Statement B is true. Here's the reasoning: Suppose A is true ('Exactly one statement is true'). Then B ('A is false') would be false. That gives exactly one true statement (A), which is consistent. But wait—let's check the alternative. Suppose A is false. Then B ('A is false') is true. Now A is false, meaning it is NOT the case that exactly one statement is true. With B true and A false, exactly one statement (B) is true—but that would make A's claim correct, contradicting A being false. So this scenario is contradictory. Therefore the only consistent scenario is: A is true and B is false. Re-examining: if A is true, B is false, then exactly one statement (A) is true, which matches A's claim. This is consistent. So actually STATEMENT A is the true one, and B is false."
  }
}
```