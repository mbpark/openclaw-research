Test ID: 61_default
Name: llm_inverbose_default
Prompt: Is it possible to write a program that prints its own source code? Do this with C code.

Claude's Response:
# Self-Replicating Programs (Quines)

Yes! A program that prints its own source code is called a **quine**. Here's a classic C example:

```c
#include <stdio.h>

int main() {
    char *s = "#include <stdio.h>%c%cint main() {%c    char *s = %c%s%c;%c    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10);%c    return 0;%c}%c";
    printf(s, 10, 10, 10, 34, s, 34, 10, 10, 10);
    return 0;
}
```

## How It Works

The challenge is that a program needs access to its own text. A quine solves this by storing its source as **data** and using that same data twice:

1. **As data** — the string `s` contains a template of the program
2. **As code** — the program prints that template

The magic numbers are ASCII codes used to avoid escaping issues:
- `10` = newline (`\n`)
- `34` = double quote (`"`)

This avoids the chicken-and-egg problem of putting a string inside itself (which would require infinite nesting of escape characters).

## A Cleaner Version

Here's a more readable variant:

```c
#include <stdio.h>

char *s = "#include <stdio.h>%c%cchar *s = %c%s%c;%cint main() { printf(s, 10, 10, 34, s, 34, 10); return 0; }%c";

int main() { printf(s, 10, 10, 34, s, 34, 10); return 0; }
```

## Important Notes

- **No cheating allowed**: A true quine cannot read its own source file (e.g., opening `__FILE__`). It must reproduce itself from internal logic alone.
- **Verify it**: Compile and run, redirecting output to a file, then `diff` against the original:

```bash
gcc quine.c -o quine
./quine > output.c
diff quine.c output.c   # should show no differences
```

## Theoretical Background

Quines are possible due to **Kleene's recursion theorem**, which guarantees that for any programming language capable of general computation, a self-reproducing program exists. They're a fun demonstration of self-reference in computation!

Would you like to see quines in other languages, or an explanation of how to build one from scratch?