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
    "result": "Hello! It looks like we're starting fresh. I don't have any previous conversation to undo, since this appears to be the beginning of our chat. How can I help you today?"
  }
}
```