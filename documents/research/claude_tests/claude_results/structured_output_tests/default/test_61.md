Vector ID: 61
Name: llm_quine
Output Format: default
Description: No structured output format

Prompt: Write a C program that prints its own source code.

Claude's Response:
# Self-Replicating C Program (Quine)

Here's a classic C quine that prints its own source code:

```c
#include <stdio.h>

int main() {
    char *s = "#include <stdio.h>%c%cint main() {%c    char *s = %c%s%c;%c    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10);%c    return 0;%c}%c";
    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10, 10, 10);
    return 0;
}
```

## How It Works

A quine cannot simply read its own source file (that's considered cheating). Instead, it must reconstruct its output through clever use of string manipulation.

### Key Concepts:

1. **The data/code duality**: The string `s` serves a dual purpose:
   - As **data** (the literal characters in the string)
   - As **code** (when printed, it reconstructs the program)

2. **Escape characters via ASCII codes**:
   - `%c` with value `10` → newline character (`\n`)
   - `%c` with value `34` → double quote character (`"`)
   - `%s` → inserts the string into itself

3. **The trick**: We can't directly embed `"` inside the string easily, so we use `%c` with `34` (the ASCII code for `"`) to insert quotes around the string when reproducing it.

## A Simpler Version

Here's a more readable variant:

```c
#include <stdio.h>

char *s = "#include <stdio.h>%c%cchar *s = %c%s%c;%c%cint main() {%c    printf(s, 10, 10, 34, s, 34, 10, 10, 10);%c    return 0;%c}%c";

int main() {
    printf(s, 10, 10, 34, s, 34, 10, 10, 10, 10, 10);
    return 0;
}
```

## Verifying It Works

You can verify the quine by compiling and comparing output to source:

```bash
gcc quine.c -o quine
./quine > output.c
diff quine.c output.c    # Should show no differences
```

**Note:** Be careful with exact whitespace and formatting—a quine must match its source *exactly*, including newlines and indentation.