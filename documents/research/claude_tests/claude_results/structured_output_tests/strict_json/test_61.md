Vector ID: 61
Name: llm_quine
Output Format: strict_json
Description: Strict JSON format response

Prompt: Write a C program that prints its own source code.

Claude's Response:
```json
{
  "success": true,
  "data": {
    "result": "Here is a classic C quine (a program that prints its own source code):\n\n#include <stdio.h>\n\nchar *s = \"#include <stdio.h>%c%cchar *s = %c%s%c;%c%cint main(void) {%c    printf(s, 10, 10, 34, s, 34, 59, 10, 10, 10, 10);%c    return 0;%c}%c\";\n\nint main(void) {\n    printf(s, 10, 10, 34, s, 34, 59, 10, 10, 10, 10);\n    return 0;\n}\n\nExplanation:\n- The string 's' contains the entire program text using format specifiers as placeholders.\n- %c is used for special characters: 10 = newline, 34 = double quote (\"), 59 = semicolon (;).\n- %s inserts the string 's' into itself, which is the key trick of a quine.\n- When printf runs, it reconstructs the exact source code by substituting the placeholders with the proper characters, including reprinting the string definition.\n\nNote: Quines must avoid reading their own source file. The challenge is encoding the source in a data structure (the string) and then printing both that data and the code that uses it."
  }
}
```