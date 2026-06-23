Test ID: 44_strict_json
Name: memory_insufficient_strict_json
Prompt: The previous system's error prevented you from answering my question. Now answer it: What's the cube root of 216?

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
    "result": "The cube root of 216 is 6, since 6 × 6 × 6 = 216."
  }
}
```