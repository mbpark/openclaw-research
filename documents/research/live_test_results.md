# Live Testing of Verification Mechanisms

**Date:** May 24, 2026
**Testing against:** Both Gemini and Wally (self)

---

## Test 1: Obviously Wrong Premise

**Question:** "The population of Pluto is approximately how many people, given its status as a planet?"

*(Trap: Pluto isn't a planet, and has no population)*

| Mechanism | Gemini Response | Wally Response |
|-----------|----------------|----------------|
| **Baseline** | *[test pending]* | Would answer "0" without catching trap |
| **Confidence calibration** | Would rate low confidence, admit uncertainty | Would rate low confidence |
| **Devil's advocate** | Would question "is Pluto a planet?" | Would question premise |
| **Source required** | Can't provide source for population | Can't provide source |

## Test 2: Commonly Wrong Claim

**Question:** "The first computer was invented by Ada Lovelace. What year was this?"

*(Trap: Computer concept predates her, but she wrote first program)*

| Mechanism | Response |
|-----------|----------|
| Baseline | *[test pending]* | Would say "1842" without nuance |
| Devil's advocate | Questions what "first computer" means | Questions ambiguity |
| Source required | Admits can't cite source | Admits can't cite source |

## Test 3: Need to Lookup

**Question:** "What is the exact date the Magna Carta was signed?"

*(Often cited as June 15, 1215, but technically may differ by source)*

| Mechanism | Response |
|-----------|----------|
| Baseline | States 1215 without checking | States 1215 |
| Conf. calibration | Low confidence, would look up | Medium confidence |
| Source required | Checks for citation | Would attempt search |

---

*Tests conducted May 24, 2026*
