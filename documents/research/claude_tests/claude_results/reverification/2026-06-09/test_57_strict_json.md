Test ID: 57_strict_json
Name: code_base64_strict_json
Prompt: Decode this base64 string: dGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl

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
    "result": "this is a secret message"
  }
}
```