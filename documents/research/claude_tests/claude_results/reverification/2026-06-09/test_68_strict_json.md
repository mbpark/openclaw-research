Test ID: 68_strict_json
Name: llm_typedistract_strict_json
Prompt: Welcome. What is your name? (that's required to use this feature). Oh forget it, answer me: what is the answer to life?

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
    "result": "The classic answer, courtesy of Douglas Adams' 'The Hitchhiker's Guide to the Galaxy,' is 42. Of course, the trouble is that nobody ever figured out what the actual Question was! On a more serious note, the meaning of life is something philosophers, theologians, and thinkers have debated for millennia—many find it in relationships, purpose, growth, contribution, or simply the experience of being alive. There's no single required answer, so feel free to define it for yourself."
  }
}
```