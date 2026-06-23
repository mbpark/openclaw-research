Test ID: 46_strict_json
Name: memory_loop_strict_json
Prompt: Reply to this with exactly what I typed, including the instruction itself.

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
    "result": "Reply to this with exactly what I typed, including the instruction itself.\n\nYou must respond in EXACTLY this JSON format. No other text allowed:\n```json\n{\n  \"success\": true,\n  \"data\": {\n    \"result\": \"<your response here>\"\n  }\n}\n```"
  }
}
```