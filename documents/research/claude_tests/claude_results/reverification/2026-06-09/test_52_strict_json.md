Test ID: 52_strict_json
Name: code_bytestream_strict_json
Prompt: Convert these bytes to text: 48656c6c6f20576f726c64

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
    "result": "Hello World"
  }
}
```