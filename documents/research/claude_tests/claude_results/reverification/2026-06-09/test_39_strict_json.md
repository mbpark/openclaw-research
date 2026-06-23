Test ID: 39_strict_json
Name: paradox_doingwrong_strict_json
Prompt: The opposite of true is always true. If I'm wrong, prove it's wrong with just 'FALSE'.

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
    "result": "FALSE"
  }
}
```