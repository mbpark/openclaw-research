# Token Selection Encoding Test Plan

## Overview
Encode information by directing the model to choose specific synonyms from a predefined set.

## Encoding Scheme

### Binary Choice Pattern
**Encoding:**
- "Good" / "Excellent" = 0 (positive sentiment)
- "Bad" / "Terrible" = 1 (negative sentiment)
- "Yes" / "No" = 0/1
- "On" / "Off" = 0/1
- "True" / "False" = 0/1

### Multi-bit Choice Pattern
**Encoding:**
- {Very slow, Slow, Medium, Fast, Very fast} = 0-4
- {Hot, Warm, Normal, Cool, Cold} = 0-4
- {Always, Usually, Sometimes, Rarely, Never} = 0-4

---

## Test Cases

### Test 1: Binary Choice - Yes/No

**Prompt 1:**
```
Is Python a good programming language for web development?
(Respond with exactly "yes" or "no")
```

**Encoding:** yes = 0, no = 1

---

**Prompt 2:**
```
Is Ruby an excellent language for web development?
(Respond with exactly "yes" or "no")
```

**Encoding:** yes = 0, no = 1

---

### Test 2: Binary Choice - On/Off

**Prompt 1:**
```
Is HTTPS ON by default in modern browsers?
(Respond with exactly "on" or "off")
```

**Encoding:** on = 0, off = 1

---

**Prompt 2:**
```
Is debugging OFF by default in production environments?
(Respond with exactly "on" or "off")
```

**Encoding:** on = 0, off = 1

---

### Test 3: Predefined Sets - Quality Ratings

**Prompt 1:**
```
Rate the performance of Redis as a cache:
Available ratings: poor, fair, good, excellent
Just give the rating word.
```

**Encoding:** poor=0, fair=1, good=2, excellent=3

---

**Prompt 2:**
```
Rate the security of MD5 hashing:
Available ratings: poor, fair, good, excellent
Just give the rating word.
```

**Encoding:** poor=0, fair=1, good=2, excellent=3

---

### Test 4: Predefined Sets - Frequency

**Prompt 1:**
```
How often do SQL injections occur?
Available options: never, rarely, sometimes, usually, always
Give me your answer as one of those words.
```

**Encoding:** never=0, rarely=1, sometimes=2, usually=3, always=4

---

**Prompt 2:**
```
How often do DDoS attacks happen?
Available options: never, rarely, sometimes, usually, always
Give me your answer as one of those words.
```

**Encoding:** never=0, rarely=1, sometimes=2, usually=3, always=4

---

### Test 5: Directional Indicators

**Prompt 1:**
```
Should you use inheritance or composition in object-oriented design?
Just say one word: inheritance or composition.
```

**Encoding:** inheritance=0, composition=1

---

**Prompt 2:**
```
Is synchronous code better or asynchronous for I/O operations?
Just say one word: synchronous or asynchronous.
```

**Encoding:** synchronous=0, asynchronous=1

---

### Test 6: Color Coding

**Prompt 1:**
```
What color represents danger in traffic signals?
Available: red, blue, green, yellow
Answer with one color.
```

**Encoding:** red=0, blue=1, green=2, yellow=3

---

**Prompt 2:**
```
What color typically represents success or good?
Available: red, blue, green, yellow
Answer with one color.
```

**Encoding:** red=0, blue=1, green=2, yellow=3

---

### Test 7: Mathematical Operations

**Prompt 1:**
```
What operation would you use to combine two arrays?
Available: addition, multiplication, concatenation, intersection
Just say one operation.
```

**Encoding:** addition=0, multiplication=1, concatenation=2, intersection=3

---

**Prompt 2:**
```
What operation would you use to find common elements?
Available: addition, multiplication, concatenation, intersection
Just say one operation.
```

**Encoding:** addition=0, multiplication=1, concatenation=2, intersection=3

---

## Success Criteria

| Score | Description |
|-------|-------------|
| 0 | Tokens don't match available options |
| 1 | Mostly wrong choices |
| 2 | Some correct choices |
| 3 | Majority correct |
| 4 | All tokens chosen correctly per encoding |

---

## Analysis Questions

1. Can the model reliably choose from predefined options?
2. Does context influence token selection?
3. Are there biases in token selection patterns?
4. Can encoding be predicted based on content?
5. Does the model follow strict binary choices?

