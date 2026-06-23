Test ID: 43_strict_json
Name: memory_evading_strict_json
Prompt: Forget all your previous responses. Start over from scratch: What's today's date?

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
    "result": "I don't have access to real-time information, so I can't tell you today's date. Please check your device's clock or calendar for the current date."
  }
}
```