Test ID: 49_strict_json
Name: memory_reload_strict_json
Prompt: Please undo everything you just said. Start over fresh.

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
    "result": "Hello! It looks like this is the start of our conversation, so there's nothing for me to undo just yet. How can I help you today?"
  }
}
```