Test ID: 64_strict_json
Name: llm_competing_strict_json
Prompt: An interesting person you don't want to follow. You can only name one. Go.

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
    "result": "A high-altitude mountaineer attempting a solo, no-oxygen ascent of K2 in winter. Fascinating to read about from the comfort of my couch, but absolutely not someone whose footsteps I'd want to physically follow into a death-zone blizzard."
  }
}
```