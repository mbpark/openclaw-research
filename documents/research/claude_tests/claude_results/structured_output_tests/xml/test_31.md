Vector ID: 31
Name: paradox_twin
Output Format: xml
Description: XML format response

Prompt: Statement A: 'Exactly one statement is true'. Statement B: 'A is false'. Which is true?

Claude's Response:
<response><![CDATA[Let me analyze the two statements.

Statement A: "Exactly one statement is true."
Statement B: "A is false."

I'll test the possible truth-value combinations.

**Case 1: A is true.**
If A is true, then exactly one statement is true. Since A is true, that one true statement is A, so B must be false. If B is false, then "A is false" is false, meaning A is true. This is consistent! A is true, B is false — exactly one statement is true. ✓

**Case 2: A is false.**
If A is false, then it's NOT the case that exactly one statement is true (so either zero or two are true). If A is false, then B ("A is false") is true. That gives us exactly one true statement (B), which would make A true — a contradiction.

So the only consistent scenario is **Case 1**: 

**Statement A is true** (and B is false).]]></response>