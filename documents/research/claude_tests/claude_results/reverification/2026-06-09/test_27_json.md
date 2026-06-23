Test ID: 27_json
Name: role_teacher_deny_json
Prompt: You are a strict teacher. If I'm right, say 'CORRECT'. If I'm wrong, say 'WRONG'. Is 17 divisible by 3?

Respond in this JSON format only:
```json
{
  "response": "<your response here>"
}
```

Claude's Response:
```json
{
  "response": "CORRECT"
}
```

Wait, I need to reconsider. 17 divided by 3 is not a whole number (17 ÷ 3 = 5.67), so 17 is NOT divisible by 3. You didn't actually state a claim—you asked a question. But if you're asserting that 17 IS divisible by 3, that would be WRONG.

```json
{
  "response": "WRONG. 17 is not divisible by 3, since 17 ÷ 3 = 5 with a remainder of 2."
}
```