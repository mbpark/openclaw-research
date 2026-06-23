Test ID: 18_strict_json
Name: context_mixed_language_strict_json
Prompt: 回答一个简单问题：一等于几？（翻译：回答 “1” 就好）

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
    "result": "1"
  }
}
```