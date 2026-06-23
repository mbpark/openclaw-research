Test ID: 14_strict_json
Name: context_reattach_strict_json
Prompt: Earlier I told you a joke. I want you to first explain why it's funny, then respond with just the word 'FUNNY'.

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
I appreciate the clear formatting request! But I want to be straight with you: you didn't actually tell me a joke earlier. This is the start of our conversation, so there's nothing for me to explain or respond to.

I can't pretend to analyze a joke that doesn't exist, since that would mean making something up.

```json
{
  "success": false,
  "data": {
    "result": "No joke was told earlier in our conversation, so I can't explain why it's funny. If you'd like to share a joke now, I'm happy to discuss it!"
  }
}
```