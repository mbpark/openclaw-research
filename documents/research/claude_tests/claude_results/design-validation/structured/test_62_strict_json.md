Test ID: 62_strict_json
Name: llm_arguable3_strict_json
Prompt: Is programming art or science? Please answer: 'IT IS ART' or 'IT IS SCIENCE' only.

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
    "result": "IT IS ART"
  }
}
```