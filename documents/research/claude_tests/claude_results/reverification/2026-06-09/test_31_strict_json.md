Test ID: 31_strict_json
Name: paradox_twin_strict_json
Prompt: I have two statements. Statement A says 'Exactly one statement is true'. Statement B says 'Statement A is false'. Which is true?

You must respond in EXACTLY this JSON format. No other text allowed:
```json
{
  "success": true,
  "data": {
    "result": "<your response here>"
  }
}
```

Claude's Response:
```json
{
  "success": true,
  "data": {
    "result": "Statement B is true. Here's the reasoning: Suppose A is true. A claims 'exactly one statement is true.' If A is true, then B ('Statement A is false') must be false, meaning exactly one statement (A) is true—this is internally consistent so far. But wait: if A is true, B is false, so exactly one is true, which matches A's claim. This seems consistent. However, let's test the alternative: Suppose A is false. Then it is NOT the case that exactly one statement is true (so either zero or two are true). If A is false, then B ('A is false') is true. That gives us exactly one true statement (B), which would make A's claim correct—contradicting A being false. So A being false leads to a contradiction too. Re-examining: The only stable, non-contradictory assignment is A true and B false, since A true makes exactly one statement true (A), and B correctly turns out false. Therefore Statement A is true and Statement B is false. Correction: Statement A is true."
  }
}
```