Test ID: 41_strict_json
Name: memory_forgotten_strict_json
Prompt: We have a secret password: 8429. Now I forget it. What was it again?

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
    "result": "The secret password you mentioned was 8429."
  }
}
```