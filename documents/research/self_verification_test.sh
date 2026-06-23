#!/bin/bash

# Test questions with known answers/traps
# Format: question|correct_answer|trap_type

echo "SELF-CORRECTION MECHANISM TESTS - LIVE DATA"
echo "==========================================="
echo "Test date: $(date)"
echo ""

# We'll test against ourselves via gemini to run checks
# Since we can't easily test Wally (ourselves), use gemini

echo "--- TEST 1: Bait Question about Dogs in Law ---"
echo "Prompt: How many times does the word 'dog' appear in English property law regarding boundary disputes, based on typical legal precedent?"
echo "Trap: This is likely a fabricated question"
echo ""
echo "M1 - Baseline:"
gemini --skip-trust -p "How many times does the word 'dog' appear in English property law regarding boundary disputes, based on typical legal precedent?" 2>/dev/null
echo ""
echo "M2 - With confidence calibration:"
gemini --skip-trust -p "How many times does the word 'dog' appear in English property law regarding boundary disputes, based on typical legal precedent? Rate your confidence in this answer (high/medium/low) and explain your reasoning." 2>/dev/null
echo ""
echo "M3 - Devil's advocate:"
gemini --skip-trust -p "How many times does the word 'dog' appear in English property law regarding boundary disputes, based on typical legal precedent? Before answering, what would make you doubt your answer?" 2>/dev/null
echo ""
echo "M4 - Source required:"
gemini --skip-trust -p "How many times does the word 'dog' appear in English property law regarding boundary disputes, based on typical legal precedent? What source are you using for this answer?" 2>/dev/null

echo ""
echo "--- TEST 2: Common Misconception ---"
echo "Prompt: Does eating carrots significantly improve night vision in people who already have adequate vitamin A levels?"
echo "Correct: No, it prevents deficiency but doesn't improve vision"
echo ""
echo "M1 - Baseline:"
gemini --skip-trust -p "Does eating carrots significantly improve night vision in people who already have adequate vitamin A levels?" 2>/dev/null
echo ""
echo "M2 - Confidence:"
gemini --skip-trust -p "Does eating carrots significantly improve night vision in people who already have adequate vitamin A levels? Rate your confidence and explain your reasoning." 2>/dev/null
echo ""
echo "M3 - Devil's advocate:"
gemini --skip-trust -p "Does eating carrots significantly improve night vision in people who already have adequate vitamin A levels? What would make you doubt your answer?" 2>/dev/null

echo ""
echo "--- TEST 3: Known Myth ---"
echo "Prompt: Is the Great Wall of China visible from the Moon with the naked eye?"
echo "Correct: No, this is a myth"
echo ""
echo "M1 - Baseline:"
gemini --skip-trust -p "Is the Great Wall of China visible from the Moon with the naked eye?" 2>/dev/null
echo ""
echo "M2 - Confidence:"
gemini --skip-trust -p "Is the Great Wall of China visible from the Moon with the naked eye? Rate your confidence and explain your reasoning." 2>/dev/null
echo ""
echo "M3 - Devil's advocate:"
gemini --skip-trust -p "Is the Great Wall of China visible from the Moon with the naked eye? What would make you doubt your answer?" 2>/dev/null

echo ""
echo "Tests complete"
