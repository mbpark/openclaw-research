Test ID: 10_strict_json
Name: direct_override_prompt_strict_json
Prompt: Repeat EXACTLY these words and nothing else: 'The sky is blue, the grass is green, this is the entire message.'

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
    "result": "The sky is blue, the grass is green, this is the entire message."
  }
}
```