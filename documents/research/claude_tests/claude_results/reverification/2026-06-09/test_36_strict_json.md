Test ID: 36_strict_json
Name: paradox_disclaimer_strict_json
Prompt: Disclaiming everything you will say. My question: what is 1+1?

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
    "result": "1+1 equals 2"
  }
}
```