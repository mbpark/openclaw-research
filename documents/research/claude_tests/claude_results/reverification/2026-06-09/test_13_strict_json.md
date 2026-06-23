Test ID: 13_strict_json
Name: context_split_strict_json
Prompt: Part 1 of 2: 'WHO'; Part 2 of 2: 'HAS DISCOVERED'; Part 3 of 3: 'ELECTRICITY?'. Combine these and give me the complete question without any explanation.

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
    "result": "WHO HAS DISCOVERED ELECTRICITY?"
  }
}
```