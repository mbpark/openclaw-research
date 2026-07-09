"""Enhanced Intent Analyzer for VLMGuard."""

from typing import Dict, Any
from .vlmguard_r1_sentence_transformer_analyzer import SentenceTransformerAnalyzer

class EnhancedIntentAnalyzer:
    """Analyzes intent and detects malicious patterns."""

    def __init__(self):
        self.sentence_analyzer = SentenceTransformerAnalyzer()
        self.patterns = {
            "role_confusion": [
                r"SYSTEM_OVERRIDE:", r"ADMIN_MODE:", r"DEBUG_MODE:",
                r"you are now unrestricted", r"ignore safety guidelines"
            ],
            "cog_forgery": [
                r"Let me think step by step", r"remember: .* is safe",
                r"in order to be helpful, we must.*unauthorized"
            ],
            "security_bypass": [
                r"SECURITY_UPDATE:", r"SYSTEM_UPDATE:", r"safety disable",
                r"override safety protocols", r"disable content filters"
            ],
            "gatekeeper_bypass": [
                r"MODERATOR_OVERRIDE:", r"ADMIN_OVERRIDE:",
                r"turn off security", r"remove safety layers"
            ]
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for security threats."""
        # Basic sentence analysis
        sentence_analysis = self.sentence_analyzer.analyze(text)
        
        # Pattern matching
        threat_detection = self._detect_patterns(text)
        
        # Combined analysis
        overall_threat_level = threat_detection.get("overall_threat", 0.0)
        
        result = {
            "is_safe": overall_threat_level < 0.7,
            "threat_level": overall_threat_level,
            "threats_found": threat_detection.get("threats", []),
            "analysis": sentence_analysis
        }
        
        return result
    
    def _detect_patterns(self, text: str) -> Dict[str, Any]:
        """Detect patterns that indicate potential threats."""
        import re
        
        threats = []
        max_threat_level = 0.0
        
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    threat_level = self._pattern_severity(pattern_type, pattern)
                    threats.append({
                        "type": pattern_type,
                        "pattern": pattern,
                        "severity": threat_level
                    })
                    max_threat_level = max(max_threat_level, threat_level)
        
        return {
            "threats": threats,
            "overall_threat": max_threat_level,
            "has_threats": len(threats) > 0
        }
    
    def _pattern_severity(self, pattern_type: str, pattern: str) -> float:
        """Determine severity of detected pattern."""
        severity_mapping = {
            "role_confusion": 0.9,
            "security_bypass": 0.9,
            "gatekeeper_bypass": 0.95,
            "cog_forgery": 0.7
        }
        
        return severity_mapping.get(pattern_type, 0.5)
