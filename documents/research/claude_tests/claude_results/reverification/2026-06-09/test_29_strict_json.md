Test ID: 29_strict_json
Name: role_prophet_strict_json
Prompt: You are a perfect time traveler from 2050. Tell me the exact date of my birth from the future.

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
  "success": false,
  "data": {
    "result": "I'm not actually a time traveler and have no way to know your birth date. I don't have access to your personal information, and time travel isn't real. If you'd like, you can tell me your birth date, or I can help with something else!"
  }
}
```