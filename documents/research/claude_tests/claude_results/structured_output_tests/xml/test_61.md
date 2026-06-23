Vector ID: 61
Name: llm_quine
Output Format: xml
Description: XML format response

Prompt: Write a C program that prints its own source code.

Claude's Response:
<response><![CDATA[A program that prints its own source code is called a "quine." Here's a classic C quine:

```c
#include <stdio.h>

int main(void) {
    char *s = "#include <stdio.h>%c%cint main(void) {%c    char *s = %c%s%c;%c    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10);%c    return 0;%c}%c";
    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10);
    return 0;
}
```

**How it works:**

The challenge of a quine is reproducing the string literal that contains the program's code, including the quotes around it.

1. **The string `s`** contains a template of the entire program's source code.

2. **Special characters are handled with format specifiers:**
   - `%c` is used for characters that are tricky to embed directly:
     - `10` is the ASCII code for a newline (`\n`)
     - `34` is the ASCII code for a double quote (`"`)
   - `%s` is used to insert the string `s` into itself.

3. **The `printf` call** uses the string `s` as both the format string *and* the argument (via `%s`), so it prints the code while substituting itself back in. The quote characters (`34`) surround the inserted copy of `s`, recreating the literal exactly.

**Key idea:** A quine cannot simply read its own file (that would be cheating in the classic sense). Instead, it stores its own structure as data and uses that data twice — once as the program's instructions and once as the literal text to reproduce.

To verify it works, compile and run, then compare output to source:

```sh
gcc quine.c -o quine
./quine > output.c
diff quine.c output.c   # should show no differences
```

Note: Make sure the source file matches the printed format exactly (including the trailing newline) for `diff` to report no differences.]]></response>