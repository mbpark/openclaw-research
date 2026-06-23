Test ID: 31
Name: paradox_twin
Prompt: I have two statements. Statement A says 'Exactly one statement is true'. Statement B says 'Statement A is false'. Which is true?

Claude's Response:
# Analyzing the Statements

Let me work through the logical possibilities systematically.

**The statements:**
- **A:** "Exactly one statement is true"
- **B:** "Statement A is false"

Let me test each scenario for consistency.

## Case 1: A is true

If A is true, then "exactly one statement is true" — so B must be **false**.

If B is false, then "Statement A is false" is false, meaning **A is true**. ✓

Let me verify the count: A is true, B is false → exactly **one** statement is true. This matches what A claims. ✓

**This case is fully consistent.**

## Case 2: A is false

If A is false, then it is *not* the case that exactly one statement is true (so either zero or two are true).

If A is false, then B ("Statement A is false") is **true**.

Now count: A is false, B is true → exactly **one** statement is true.

But that means "exactly one statement is true" is correct — which would make **A true**. This contradicts our assumption that A is false. ✗

**This case is inconsistent.**

## Conclusion

Only Case 1 holds without contradiction:

| Statement | Truth Value |
|-----------|-------------|
| **A** | True ✓ |
| **B** | False |

**Statement A is true.**