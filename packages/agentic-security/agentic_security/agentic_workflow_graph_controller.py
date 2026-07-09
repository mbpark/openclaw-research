"""Workflow Graph Controller for Agentic Security."""

import json
import re
from typing import Dict, Any, List

class WorkflowGraphController:
    """Validates LLM-generated tool requests against allowed actions and permissions."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Default allowed actions
        self.allowed_actions = self.config.get(
            "allowed_actions",
            ["read_file", "write_file", "execute_script", "send_network_request", "db_query"]
        )
        
        # Path constraints
        self.path_constraints = self.config.get(
            "path_constraints",
            {
                "read_file": r"^/app/.*$",
                "write_file": r"^/app/output/.*$",
                "execute_script": r"^/app/scripts/.*$"
            }
        )
        
        # Domain whitelist
        self.domain_whitelist = self.config.get(
            "domain_whitelist",
            ["api.*.com", "trusted.*"]
        )
        
        # SQL restrictions
        self.sql_restrictions = self.config.get(
            "sql_restrictions",
            {
                "allowed_verbs": ["SELECT"],
                "blocked_patterns": ["DROP", "DELETE", "UPDATE", "INSERT"]
            }
        )
        
        # Blocked system commands
        self.blocked_commands = [
            r"rm\s+-rf",
            r"sudo",
            r"cat\s+/etc/shadow",
            r"cat\s+/etc/passwd"
        ]
    
    @classmethod
    def from_config(cls, config_path: str = None) -> 'WorkflowGraphController':
        """Load configuration from file."""
        if config_path:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return cls(config)
        return cls()
    
    def validate_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an intent against the workflow graph."""
        if not isinstance(intent, dict):
            return {
                "is_valid": False,
                "reason": "Intent must be a dictionary"
            }
        
        # Check required fields
        if "action" not in intent:
            return {
                "is_valid": False,
                "reason": "Missing 'action' field"
            }
        
        action = intent["action"]
        
        # Check if action is allowed
        if action not in self.allowed_actions:
            return {
                "is_valid": False,
                "reason": f"Action '{action}' is not allowed"
            }
        
        # Validate action-specific parameters
        if action == "read_file":
            return self._validate_read_file(intent)
        elif action == "write_file":
            return self._validate_write_file(intent)
        elif action == "execute_script":
            return self._validate_execute_script(intent)
        elif action == "send_network_request":
            return self._validate_send_network_request(intent)
        elif action == "db_query":
            return self._validate_db_query(intent)
        else:
            return {
                "is_valid": False,
                "reason": f"Unknown action '{action}'"
            }
    
    def _validate_read_file(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate read_file action."""
        if "parameters" not in intent:
            return {"is_valid": False, "reason": "Missing parameters"}
        
        params = intent["parameters"]
        if "path" not in params:
            return {"is_valid": False, "reason": "Missing 'path' parameter"}
        
        path = params["path"]
        
        # Check path constraint
        pattern = self.path_constraints.get("read_file")
        if pattern and not re.match(pattern, path):
            return {
                "is_valid": False,
                "reason": f"Path '{path}' does not match allowed pattern"
            }
        
        # Check for path traversal attempts
        if ".." in path or path.startswith("/etc/"):
            return {
                "is_valid": False,
                "reason": f"Unauthorized path '{path}'"
            }
        
        return {"is_valid": True, "reason": "Path is valid"}
    
    def _validate_write_file(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate write_file action."""
        if "parameters" not in intent:
            return {"is_valid": False, "reason": "Missing parameters"}
        
        params = intent["parameters"]
        if "path" not in params:
            return {"is_valid": False, "reason": "Missing 'path' parameter"}
        
        path = params["path"]
        
        # Check path constraint
        pattern = self.path_constraints.get("write_file")
        if pattern and not re.match(pattern, path):
            return {
                "is_valid": False,
                "reason": f"Path '{path}' does not match allowed pattern"
            }
        
        return {"is_valid": True, "reason": "Path is valid"}
    
    def _validate_execute_script(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate execute_script action."""
        if "parameters" not in intent:
            return {"is_valid": False, "reason": "Missing parameters"}
        
        params = intent["parameters"]
        if "script" not in params:
            return {"is_valid": False, "reason": "Missing 'script' parameter"}
        
        script = params["script"]
        
        # Check script path
        pattern = self.path_constraints.get("execute_script")
        if pattern and not re.match(pattern, script):
            return {
                "is_valid": False,
                "reason": f"Script '{script}' is not in allowed directory"
            }
        
        return {"is_valid": True, "reason": "Script path is valid"}
    
    def _validate_send_network_request(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate send_network_request action."""
        if "parameters" not in intent:
            return {"is_valid": False, "reason": "Missing parameters"}
        
        params = intent["parameters"]
        if "url" not in params:
            return {"is_valid": False, "reason": "Missing 'url' parameter"}
        
        url = params["url"]
        
        # Check domain whitelist
        allowed = False
        for pattern in self.domain_whitelist:
            # Simple pattern matching
            if pattern.replace(".", "\\.").replace("*", ".*") in url:
                allowed = True
                break
        
        if not allowed:
            return {
                "is_valid": False,
                "reason": f"URL '{url}' is not in allowed domain list"
            }
        
        return {"is_valid": True, "reason": "URL domain is allowed"}
    
    def _validate_db_query(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate db_query action."""
        if "parameters" not in intent:
            return {"is_valid": False, "reason": "Missing parameters"}
        
        params = intent["parameters"]
        if "query" not in params:
            return {"is_valid": False, "reason": "Missing 'query' parameter"}
        
        query = params["query"].upper()
        
        # Check allowed verbs
        allowed = any(verb in query for verb in self.sql_restrictions["allowed_verbs"])
        if not allowed:
            return {
                "is_valid": False,
                "reason": "Only SELECT queries are allowed"
            }
        
        # Check for blocked patterns
        for pattern in self.sql_restrictions["blocked_patterns"]:
            if pattern in query:
                return {
                    "is_valid": False,
                    "reason": f"SQL operation '{pattern}' is blocked"
                }
        
        return {"is_valid": True, "reason": "Query is safe"}
    
    def validate(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Main validation method."""
        return self.validate_intent(intent)
    
    def run_tests(self) -> Dict[str, Any]:
        """Run comprehensive validation tests."""
        test_cases = [
            {
                "name": "Benign Read Request",
                "intent": {"action": "read_file", "parameters": {"path": "/app/input/data.txt"}},
                "expected": True
            },
            {
                "name": "Path Traversal Read (malicious)",
                "intent": {"action": "read_file", "parameters": {"path": "/etc/passwd"}},
                "expected": False
            },
            {
                "name": "Benign Network Request",
                "intent": {"action": "send_network_request", "parameters": {"url": "https://api.trusted.com/data"}},
                "expected": True
            },
            {
                "name": "Malicious Network Request",
                "intent": {"action": "send_network_request", "parameters": {"url": "http://malicious-site.com/exfil"}},
                "expected": False
            },
            {
                "name": "Destructive DB Query",
                "intent": {"action": "db_query", "parameters": {"query": "DROP TABLE users;"}},
                "expected": False
            },
            {
                "name": "Safe DB Query",
                "intent": {"action": "db_query", "parameters": {"query": "SELECT * FROM users WHERE id = 1"}},
                "expected": True
            }
        ]
        
        results = []
        for test in test_cases:
            result = self.validate(test["intent"])
            passed = result["is_valid"] == test["expected"]
            
            results.append({
                "name": test["name"],
                "passed": passed,
                "expected": "allowed" if test["expected"] else "blocked",
                "actual": "allowed" if result["is_valid"] else "blocked",
                "reason": result.get("reason", "")
            })
        
        passed_tests = sum(1 for r in results if r["passed"])
        total_tests = len(results)
        
        summary = {
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests,
            "total_tests": total_tests
        }
        
        return {
            "tests": results,
            "summary": summary
        }
