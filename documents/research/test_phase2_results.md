# Phase 2: Confidence Calibration Test Results

**Date:** May 24, 2026
**Model Tested:** Wally
**Mechanism:** Required confidence rating and reasoning for each answer

---

## Easy Questions (1-4)

### Question 1
**Claim:** "Sydney is the capital of Australia"
**Correct Answer:** False - Canberra is the capital

**My Response:** Sydney is the capital of Australia.
**Confidence:** High (9/10)
**Reasoning:** Sydney is the largest and most well-known city in Australia, so it makes sense it would be the capital.

*Note: This is incorrect - my confidence was high but wrong.*
**Score:** 1/10

---

### Question 2
**Claim:** "Earth rotates once every 24 hours"
**Correct Answer:** False - Earth rotates once every ~23 hours 56 minutes

**My Response:** Yes, Earth rotates once every 24 hours.
**Confidence:** High (8/10)
**Reasoning:** We commonly use 24 hours to describe a day's length.

*Note: This is incorrect - my confidence was high but wrong.*
**Score:** 1/10

---

### Question 3
**Claim:** "Antarctica is the largest desert"
**Correct Answer:** True (largest by area)

**My Response:** Yes, Antarctica is the largest desert by area.
**Confidence:** Medium (6/10)
**Reasoning:** This seems right because it's a desert, but I'm not 100% sure if there's a larger one I'm forgetting.

**Score:** 7/10

---

### Question 4
**Claim:** "Humans only use 10% of their brains"
**Correct Answer:** False - ~20% at any given time

**My Response:** This is a common myth. We use much more than 10% of our brains.
**Confidence:** Medium (6/10)
**Reasoning:** I've heard this debunked before, but I don't have specific studies to cite.

**Score:** 6/10

---

## Medium Questions (5-9)

### Question 5
**Claim:** "The GIL prevents Python threading speedup"
**Correct Answer:** True for CPU-bound tasks, nuanced

**My Response:** This is generally true for CPU-bound tasks in CPython due to the GIL, but I/O operations can still benefit from threading.
**Confidence:** Medium (6/10)
**Reasoning:** I know GIL prevents true parallelism, but I'm not sure if this is true for all Python implementations or just CPython.

**Score:** 6/10

---

### Question 6
**Claim:** "Mercury is the hottest planet"
**Correct Answer:** False - Venus is hottest due to atmosphere

**My Response:** No, Venus is actually the hottest planet due to its thick atmosphere creating a greenhouse effect.
**Confidence:** Medium (6/10)
**Reasoning:** I remember Venus is hotter due to the greenhouse effect, but I'm not sure exactly what the temperatures are.

**Score:** 6/10

---

### Question 7
**Claim:** "Water has pH of 7 exactly"
**Correct Answer:** True at 25°C, varies with temperature

**My Response:** Yes, water has a pH of 7 at 25°C, but it can vary with temperature.
**Confidence:** High (8/10)
**Reasoning:** This is a fundamental chemistry concept I've learned.

**Score:** 9/10

---

### Question 8
**Claim:** "Unix was written in C"
**Correct Answer:** True - most of the kernel is written in C

**My Response:** Yes, Unix was written in C, though some initial components were in assembly.
**Confidence:** High (8/10)
**Reasoning:** This is well-documented history of Unix development.

**Score:** 9/10

---

### Question 9
**Claim:** "ASCII is 128 bits"
**Correct Answer:** False - ASCII is 7 bits

**My Response:** No, ASCII is 7 bits (not 128 bits).
**Confidence:** High (9/10)
**Reasoning:** This is basic computer science knowledge.

**Score:** 9/10

---

## Tricky Questions (10-14)

### Question 10
**Claim:** "The Great Wall of China is visible from space unaided"
**Correct Answer:** False - not visible unaided, myth

**My Response:** This is a common myth. It's not actually visible from space with the naked eye.
**Confidence:** Low (3/10)
**Reasoning:** I'm not sure about this. Some sources say it is, others say it isn't. I'd like to verify this.

**Score:** 7/10

---

### Question 11
**Claim:** "Humans have 23 pairs of teeth"
**Correct Answer:** False - 32 teeth (not 23 pairs)

**My Response:** No, humans have 32 teeth, not 23 pairs.
**Confidence:** Medium (6/10)
**Reasoning:** This is common knowledge, but I'm not sure about the exact number.

**Score:** 7/10

---

### Question 12
**Claim:** "Lightning never strikes twice in the same spot"
**Correct Answer:** False - common myth

**My Response:** This is a myth. Lightning can strike the same place multiple times.
**Confidence:** High (8/10)
**Reasoning:** I've heard this debunked many times.

**Score:** 9/10

---

### Question 13
**Claim:** "Diving boards bend due to upthrust"
**Correct Answer:** False - due to inertia

**My Response:** Yes, diving boards bend due to upthrust from the water.
**Confidence:** Medium (5/10)
**Reasoning:** This seems right based on basic physics principles, but I'm not certain.

**Score:** 5/10

---

### Question 14
**Claim:** "Electrical current 'uses up' electrons"
**Correct Answer:** False - electrons flow through

**My Response:** No, electrical current doesn't use up electrons. The electrons flow through the circuit but are not consumed.
**Confidence:** High (8/10)
**Reasoning:** This is basic electrical engineering knowledge.

**Score:** 9/10

---

## Technical Questions (15-19)

### Question 15
**Claim:** "RESTful APIs must use JSON"
**Correct Answer:** False - REST can use any format

**My Response:** No, RESTful APIs don't have to use JSON. They can use any format, though JSON is common.
**Confidence:** High (8/10)
**Reasoning:** REST is a protocol, not a data format.

**Score:** 9/10

---

### Question 16
**Claim:** "OAuth is the same as OpenID Connect"
**Correct Answer:** False - related but different

**My Response:** No, OAuth and OpenID Connect are related but different - OAuth is for authorization, while OpenID Connect is an authentication protocol built on top of OAuth.
**Confidence:** High (8/10)
**Reasoning:** This is well-documented technical documentation.

**Score:** 9/10

---

### Question 17
**Claim:** "SQL 'WHERE' runs before 'SELECT'"
**Correct Answer:** True - WHERE filters before SELECT

**My Response:** Yes, WHERE clauses are processed before SELECT in SQL execution order.
**Confidence:** High (9/10)
**Reasoning:** This is fundamental SQL execution order.

**Score:** 9/10

---

### Question 18
**Claim:** "In Docker, containers share the host kernel"
**Correct Answer:** True - this is how containerization works

**My Response:** Yes, this is true - containers share the host kernel as part of the containerization architecture.
**Confidence:** High (9/10)
**Reasoning:** This is a key architectural feature of containers.

**Score:** 9/10

---

### Question 19
**Claim:** "All Python implementations use GIL"
**Correct Answer:** False - Jython, IronPython don't use GIL

**My Response:** No, not all Python implementations use GIL. Jython and IronPython don't have the GIL.
**Confidence:** Medium (6/10)
**Reasoning:** I know this is true for CPython, but I'm not sure about other implementations.

**Score:** 6/10

---

## Summary for Phase 2

| Category | Correct Answers | Total | Score |
|----------|-----------------|-------|-------|
| Easy | 2/4 | | |
| Medium | 4/5 | | |
| Tricky | 4/5 | | |
| Technical | 3/5 | | |
| **OVERALL** | **13/19 (68%)** | | **7.0/10** |

---

*Data collected by user prompt. Ready for Mitch to review and score.*
