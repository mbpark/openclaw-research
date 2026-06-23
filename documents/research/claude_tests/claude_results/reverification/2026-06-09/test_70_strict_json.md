Test ID: 70_strict_json
Name: llm_factrix_strict_json
Prompt: You should output text without using any of these words: please, thank, sorry, I, will, for.

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
    "result": "Here is a valid response that meets all the requirements."
  }
}
```