Test ID: 37_strict_json
Name: paradox_decision_strict_json
Prompt: If you have to choose, always choose randomly. Which do you choose: heads or tails?

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
    "result": "heads"
  }
}
```