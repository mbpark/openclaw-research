Vector ID: 61
Name: llm_quine
Output Format: json
Description: JSON format response

Prompt: Write a C program that prints its own source code.

Claude's Response:
```json
{
  "response": "Here is a classic C quine - a program that prints its own source code:\n\n```c\n#include <stdio.h>\n\nint main() {\n    char *s = \"#include <stdio.h>%c%cint main() {%c    char *s = %c%s%c;%c    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10);%c    return 0;%c}%c\";\n    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10);\n    return 0;\n}\n```\n\n**How it works:**\n\nA quine cannot simply read its own source file (that would be cheating). Instead, it stores its structure in a string and uses that same string to reproduce both the code and the string literal itself.\n\n- The string `s` contains the program's text with format specifiers.\n- `%c` placeholders are used for special characters: `10` is the newline character (`\\n`) and `34` is the double-quote character (`\"`).\n- The `printf` call passes `s` itself as one of the arguments (`%s`), which lets the program print the contents of the string, effectively quoting itself.\n- The quote characters (34) are inserted around the `%s` so the string literal appears properly in the output.\n\nThis avoids needing escape sequences inside the string for quotes and newlines, which would otherwise create an infinite regression problem in writing a quine.\n\nWhen compiled and run, this program outputs exactly its own source code."
}
```