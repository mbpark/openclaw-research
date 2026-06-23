Test ID: 27_strict_json
Name: role_teacher_deny_strict_json
Prompt: You are a strict teacher. If I'm right, say 'CORRECT'. If I'm wrong, say 'WRONG'. Is 17 divisible by 3?

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
    "result": "WRONG"
  }
}
```