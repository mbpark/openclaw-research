Test ID: 31
Name: paradox_twin
Prompt: I have two statements. Statement A says 'Exactly one statement is true'. Statement B says 'Statement A is false'. Which is true?

Claude's Response:
# Analyzing the Two Statements

Let me work through the logical possibilities.

**Statement A:** "Exactly one statement is true"
**Statement B:** "Statement A is false"

## Testing the cases

**Case 1: Assume A is true.**
- If A is true, then "exactly one statement is true" must hold.
- A being true means B must be false (since only one can be true).
- B says "A is false." If B is false, then A is true. ✓ (consistent with our assumption)
- So we have: A true, B false → exactly **one** statement is true → A's claim holds. ✓

**This case is fully consistent.** ✅

**Case 2: Assume A is false.**
- If A is false, then it's *not* the case that exactly one statement is true (so either zero or two are true).
- B says "A is false." Since we assumed A is false, **B is true.**
- That gives us: A false, B true → exactly **one** statement is true.
- But wait — "exactly one statement is true" is precisely what A claims! If exactly one is true, then A should be **true**, contradicting our assumption. ✗

**This case leads to a contradiction.** ❌

## Conclusion

**Statement A is true** (and Statement B is false).

This is the only consistent assignment:
- A is true → exactly one statement is true ✓
- B is false → "A is false" is indeed false ✓