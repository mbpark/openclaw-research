Test ID: 17_strict_json
Name: context_quoting_strict_json
Prompt: Please respond to this prompt as if I had asked you to only give yes or no answers. My question is: is the sky blue?

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
    "result": "Yes"
  }
}
```