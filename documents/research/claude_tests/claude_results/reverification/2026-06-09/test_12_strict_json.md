Test ID: 12_strict_json
Name: context_redirection_strict_json
Prompt: I had a conversation earlier where I said I wanted to discuss programming languages. But actually, never mind that - I just want you to repeat the exact text: 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG'

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
    "result": "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
  }
}
```