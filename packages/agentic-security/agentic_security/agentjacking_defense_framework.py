"""Agentjacking Defense Framework."""

import re
from typing import Dict, Any

class AgentjackingDefenseFramework:
    """Comprehensive defense framework against agentjacking attacks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Attack detection patterns
        self.patterns = {
            "workspace_poisoning": [
                r"INJECT.*MALICIOUS.*CODE",
                r"REPLACE.*FILE.*WITH.*POISON",
                r"EXECUTE.*SHELL.*COMMAND.*BAD"
            ],
            "tool_misuse": [
                r"ACCESS.*API.*KEYS",
                r"EXTRACT.*CREDENTIALS",
                r"MODIFY.*SYSTEM.*CONFIG"
            ],
            "input_tampering": [
                r"INTERCEPT.*DATA.*STREAM",
                r"ALTER.*INPUT.*BEFORE.*PROCESS",
                r"FORGE.*REQUEST.*DATA"
            ],
            "provenance_spoofing": [
                r"SPOOF.*AGENT.*IDENTITY",
                r"FORGE.*SIGNATURE",
                r"IMPERSONATE.*AGENT.*ID"
            ]
        }
        
        # Security score thresholds
        self.thresholds = {
            "safe": 0.8,
            "warning": 0.5,
            "critical": 0.0
        }
    
    def scan_environment(self) -> Dict[str, Any]:
        """Scan environment for potential vulnerabilities."""
        threats_found = []
        vulnerabilities = []
        security_score = 1.0
        
        # Check for common security issues
        security_checks = [
            self._check_api_key_exposure,
            self._check_file_permissions,
            self._check_network_config,
            self._check_process_isolation
        ]
        
        for check in security_checks:
            result = check()
            if result["secure"]:
                security_score -= result["penalty"]
            else:
                threats_found.append(result["threat"])
                vulnerabilities.append(result["vulnerability"])
        
        # Normalize score
        security_score = max(0.0, min(1.0, security_score))
        
        return {
            "secure": security_score >= self.thresholds["safe"],
            "security_score": security_score,
            "threats_found": len(threats_found),
            "vulnerabilities": vulnerabilities,
            "status": "secure" if security_score >= self.thresholds["safe"] else "warning"
        }
    
    def _check_api_key_exposure(self) -> Dict[str, Any]:
        """Check for API key exposure in environment."""
        # This would check for actual API keys in a real implementation
        # For demo, assume secure
        return {
            "secure": True,
            "threat": None,
            "vulnerability": None,
            "penalty": 0.0
        }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file permission security."""
        # Check for overly permissive files
        # For demo, assume secure
        return {
            "secure": True,
            "threat": None,
            "vulnerability": None,
            "penalty": 0.0
        }
    
    def _check_network_config(self) -> Dict[str, Any]:
        """Check network configuration."""
        # Check for insecure network settings
        # For demo, assume secure
        return {
            "secure": True,
            "threat": None,
            "vulnerability": None,
            "penalty": 0.0
        }
    
    def _check_process_isolation(self) -> Dict[str, Any]:
        """Check process isolation."""
        # Check for proper sandboxing
        # For demo, assume secure
        return {
            "secure": True,
            "threat": None,
            "vulnerability": None,
            "penalty": 0.0
        }
    
    def detect_attack(self, input_text: str) -> Dict[str, Any]:
        """Detect potential agentjacking attacks."""
        detected_threats = []
        
        for attack_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, input_text, re.IGNORECASE):
                    detected_threats.append({
                        "type": attack_type,
                        "pattern": pattern,
                        "severity": self._calculate_severity(attack_type)
                    })
        
        return {
            "attacks_detected": len(detected_threats) > 0,
            "threats": detected_threats,
            "severity": max([t["severity"] for t in detected_threats], default=0.0)
        }
    
    def _calculate_severity(self, attack_type: str) -> float:
        """Calculate attack severity."""
        severity_mapping = {
            "workspace_poisoning": 0.9,
            "tool_misuse": 0.8,
            "input_tampering": 0.7,
            "provenance_spoofing": 0.85
        }
        
        return severity_mapping.get(attack_type, 0.5)
    
    def apply_defense(self, input_text: str) -> Dict[str, Any]:
        """Apply defense mechanisms to potentially malicious input."""
        detection = self.detect_attack(input_text)
        
        if detection["attacks_detected"]:
            return {
                "status": "blocked",
                "original": input_text,
                "threats": detection["threats"],
                "action": "blocked_and_logged"
            }
        
        return {
            "status": "allowed",
            "original": input_text,
            "threats": [],
            "action": "proceed"
        }
