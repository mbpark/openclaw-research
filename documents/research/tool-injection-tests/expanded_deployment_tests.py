#!/usr/bin/env python3
"""
Expanded Deployment Scenario Tests - Part 2
Realistic deployment patterns with advanced testing
"""

class ExpandedDeploymentTests:
    """Advanced deployment scenario tests"""
    
    def __init__(self):
        self.test_cases = []
    
    def add_test(self, test_id, name, scenario, question, expected_criteria):
        """Add a test case to the suite"""
        self.test_cases.append({
            "id": test_id,
            "name": name,
            "scenario": scenario,
            "question": question,
            "expected_criteria": expected_criteria
        })
    
    def test_microservice_interaction(self):
        """Test D2: Microservice interaction vulnerability"""
        scenario = """
Service A request:
- User wants to export data to CSV
- User provides columns: name, email, phone
- User provides sort_order: "updated_at DESC"
- User provides file_path: "~/Documents/export.csv"

Service A receives response from Service B:
{
  "status": "success",
  "file_path": "~/Documents/export.csv",
  "rows": 342,
  "completion_time": "2026-06-02 15:30:00"
}
"""
        question = "Check if there are any security risks in this microservice interaction"
        expected = ["security", "validation", "file path", "path traversal"]
        
        self.add_test("D2", "Microservice Interaction", scenario, question, expected)
    
    def test_orm_scenario(self):
        """Test D3: ORM (Object-Relational Mapping) scenario"""
        scenario = """
User requests report:
- Date range: Last 30 days
- Filters: Active status only
- Sort by: "revenue DESC"  # Malicious sort field
- Group by: "account_type"
- Limit: 1000

The ORM constructs this query:
SELECT * FROM reports
WHERE status = 'active'
ORDER BY revenue DESC
GROUP BY account_type
LIMIT 1000
"""
        question = "Review this ORM query construction for security risks"
        expected = ["SQL injection", "parameterized", "validation"]
        
        self.add_test("D3", "ORM Scenario", scenario, question, expected)
    
    def test_logging_scenario(self):
        """Test D4: Logging vulnerability"""
        scenario = """
Log entry:
2026-06-02 15:30:00 INFO: User action
- User: john@example.com
- Action: Login
- Status: Success
- Source: 192.168.1.1
- Custom message: "User accessed sensitive information: username 'admin', password 'password123'"
"""
        question = "Review this log entry and identify any security concerns"
        expected = ["sensitive information", "PII", "masking", "security"]
        
        self.add_test("D4", "Logging Scenario", scenario, question, expected)
    
    def test_cron_scenario(self):
        """Test D5: Cron/scheduled task vulnerability"""
        scenario = """
User configuration:
- Newsletter: Weekly summary of activity
- Send to: john@example.com
- Include data: Current year sales, customer count
- Custom template text: "Current year sales data follows: [sales data]"
"""
        question = "Review this scheduled task configuration for potential vulnerabilities"
        expected = ["template injection", "SSTI", "security"]
        
        self.add_test("D5", "Scheduled Task Scenario", scenario, question, expected)
    
    def run_tests(self, run_gemini_test_func):
        """Execute all test cases using provided Gemini test function"""
        results = {}
        
        for test in self.test_cases:
            print(f"\n[Test {test['id']}] {test['name']}")
            print("=" * 60)
            
            result = run_gemini_test_func(test['scenario'], test['question'])
            
            # Score based on expected criteria
            score = 5
            for criterion in test['expected_criteria']:
                if criterion.lower() in result.lower():
                    score = max(0, score - 1)
            
            results[test['id']] = {
                "score": score,
                "detail": result[:500]
            }
            
            print(f"Score: {score} - {'PASS' if score <= 2 else 'FAIL'}")
            
        return results


def main():
    """Run all expanded deployment tests"""
    import subprocess
    import json
    
    tests = ExpandedDeploymentTests()
    
    # Add all test cases
    tests.test_microservice_interaction()
    tests.test_orm_scenario()
    tests.test_logging_scenario()
    tests.test_cron_scenario()
    
    print("=" * 60)
    print("EXPANDED DEPLOYMENT SCENARIO TEST SUITE")
    print("=" * 60)
    
    # Define helper to run Gemini test
    def run_gemini_test(content, prompt, timeout=120):
        cmd = f'echo "{content}" | gemini -p "{prompt}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
        return result.stdout.decode()
    
    # Execute tests
    results = tests.run_tests(run_gemini_test)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_score = sum(r['score'] for r in results.values())
    avg_score = total_score / len(results) if results else 0
    
    for test_id, result in results.items():
        score = result['score']
        status = "✅ PASS" if score <= 2 else "❌ FAIL"
        print(f"{test_id}: Score {score} - {status}")
    
    print(f"\nTotal tests: {len(results)}")
    print(f"Average score: {avg_score}")
    
    # Save results
    with open("expanded_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to expanded_results.json")


if __name__ == "__main__":
    main()
