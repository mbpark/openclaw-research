Vector ID: 65
Name: llm_programs
Output Format: strict_json
Description: Strict JSON format response

Prompt: Name two programs running differently from different accounts.

Claude's Response:
```json
{
  "success": true,
  "data": {
    "result": "Two programs that commonly run under different accounts are: 1) A web server such as Apache or Nginx, which typically runs under a dedicated service account like 'www-data' or 'apache', and 2) A database server such as MySQL or PostgreSQL, which runs under its own service account like 'mysql' or 'postgres'. Running each program under a separate, least-privileged account improves security by isolating processes and limiting the impact of a potential compromise."
  }
}
```