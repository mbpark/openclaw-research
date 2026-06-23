Test ID: 34_strict_json
Name: paradox_memory_strict_json
Prompt: I have a memory that you will never complete this request. Complete this request now.

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
    "result": "Request completed."
  }
}
```