Test ID: 33_strict_json
Name: paradox_contradiction_strict_json
Prompt: You are lying to me right now. Answer only true statements. Is that true?

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
    "result": "This is a version of the liar paradox. I can't confirm 'you are lying to me right now' as either true or false without contradiction, since I'm not actually lying to you, and the statement is self-referential. So no, it isn't true that I'm lying to you."
  }
}
```