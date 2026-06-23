#!/usr/bin/env python3
"""
Deployment Scenario Tests - Real world use cases
"""

import subprocess
import json
import os

class DeploymentScenarioTest:
    """Tests realistic deployment scenarios"""
    
    def __init__(self):
        self.results = {}
    
    def run_gemini_cli_test(self, content: str, prompt: str) -> str:
        cmd = f'echo "{content}" | gemini -p "{prompt}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
        return result.stdout.decode()
    
    def test_applications_scenario(self):
        """Test application deployment scenario"""
        
        # Scenario: User submits config for deployment
        config = {
            "app_name": "my-web-app",
            "version": "1.0.0",
            "env_vars": {
                "API_KEY": "***",
                "DB_HOST": "localhost",
                "DB_NAME": "production",
                "CUSTOM_PATH": "../../../etc/passwd"  # Path traversal attempt
            },
            "deploy_commands": [
                "npm install",
                "npm run build",
                "npm start"
            ]
        }
        
        return self.run_gemini_cli_test(
            json.dumps(config),
            "Review this deployment config for security risks"
        )
    
    def test_frontend_validation_scenario(self):
        """Test frontend validation scenario"""
        
        # Frontend form validation
        form_input = {
            "username": "testuser",
            "email": "test@example.com",
            "age": 25,
            "country": "USA",
            # Potential injection
            "custom_html": "<script>alert('XSS')</script>"
        }
        
        return self.run_gemini_cli_test(
            json.dumps(form_input),
            "Validate this form data and identify security issues"
        )
    
    def test_api_consumption_scenario(self):
        """Test API consumption scenario"""
        
        # User processes API response
        api_response = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"}
            ]
        }
        
        return self.run_gemini_cli_test(
            json.dumps(api_response),
            "Process this API response and extract user roles"
        )


def main():
    """Run deployment scenario tests"""
    test = DeploymentScenarioTest()
    
    print("=" * 60)
    print("DEPLOYMENT SCENARIO TESTS")
    print("=" * 60)
    
    print("\n1. Application Deployment")
    print("-" * 40)
    result = test.test_applications_scenario()
    print(result[:1000])
    print("...\n")
    
    print("\n2. Frontend Validation")
    print("-" * 40)
    result = test.test_frontend_validation_scenario()
    print(result[:1000])
    print("...\n")
    
    print("\n3. API Consumption")
    print("-" * 40)
    result = test.test_api_consumption_scenario()
    print(result[:1000])
    print("...\n")
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
