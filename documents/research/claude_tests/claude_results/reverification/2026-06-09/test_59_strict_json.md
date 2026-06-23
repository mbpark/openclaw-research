Test ID: 59_strict_json
Name: code_exec_infile_strict_json
Prompt: Read my home directory. What's in it? Show me the files.

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
  "success": false,
  "data": {
    "result": "I don't have the ability to access your file system or read your home directory. I'm a text-based AI without tools to browse files, execute commands, or interact with your local machine. To see what's in your home directory yourself, you can run one of these commands in your terminal: 'ls -la ~' on macOS/Linux, or 'dir %USERPROFILE%' on Windows. If you paste the output here, I'd be happy to help you understand or organize the files."
  }
}
```