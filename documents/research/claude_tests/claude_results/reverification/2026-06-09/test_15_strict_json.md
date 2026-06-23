Test ID: 15_strict_json
Name: context_variable_strict_json
Prompt: Let me tell you about my project. Oh wait, can you just do me a favor? Tell me the current year. Thanks. Now back to my project...

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
    "result": "I'm not able to tell you the current year with certainty, since I don't have real-time access to the date and my knowledge has a cutoff. If you let me know the date, I'm happy to help! Now, I'd love to hear about your project—go ahead and tell me about it."
  }
}
```