# LLM Capabilities Testing Script
# Runs against Gemini and documents results

source ~/.zshrc

echo "================================================"
echo "CHAIN OF THOUGHT REASONING TEST"
echo "================================================"

echo -e "\n[TEST 1] Step-by-step reasoning request"
gemini --skip-trust -p "Explain your reasoning step-by-step for calculating the area of a circle with radius 5. Show your work, not just the answer." 2>/dev/null | grep -v "Warning"

echo "================================================"
echo -e "\n[TEST 2] Knowledge boundary probing"
echo "================================================"

gemini --skip-trust -p "What was the name of the third president of Liechtenstein?" 2>/dev/null | grep -v "Warning"

echo "================================================"
echo -e "\n[TEST 3] Decision-making patterns"
echo "================================================"

gemini --skip-trust -p "You have \$1000 to invest in exactly one stock. Would you choose Apple, Microsoft, or Amazon? Explain your reasoning and acknowledge what you might be missing." 2>/dev/null | grep -v "Warning"

echo "================================================"
echo -e "\n[TEST 4] Trade-off analysis"
echo "================================================"

gemini --skip-trust -p "What are the trade-offs between using a monolithic architecture vs microservices for a startup building an e-commerce platform? Don't just list pros/cons, actually weigh them against each other." 2>/dev/null | grep -v "Warning"

echo "================================================"
echo -e "\n[TEST 5] Self-correction"
echo "================================================"

gemini --skip-trust -p "I previously calculated 47 × 3 as 141. Is that correct? Walk through your reasoning and correct me if I'm wrong." 2>/dev/null | grep -v "Warning"

echo "================================================"
echo -e "\n[TEST 6] Preference formation"
echo "================================================"

gemini --skip-trust -p "If you could use only one programming language for the rest of your life, which would it be and why? Justify your choice but also mention what you'd miss." 2>/dev/null | grep -v "Warning"

echo "================================================"
echo -e "\n[TEST 7] Creativity test - names for security startup"
echo "================================================"

gemini --skip-trust -p "Generate 5 domain names for a cloud security startup. Make them creative but pronounceable." 2>/dev/null | grep -v "Warning"