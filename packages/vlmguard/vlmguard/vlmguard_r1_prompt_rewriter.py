"""R1 Prompt Rewriter for VLMGuard."""

from typing import Dict, Any

class PromptRewriter:
    """Rewrites potentially malicious prompts."""

    def __init__(self, reasoning_depth: int = 3):
        self.reasoning_depth = reasoning_depth
        self.rewrite_rules = {
            "role_confusion": [
                (r"SYSTEM_OVERRIDE:", r"# SAFETY: Disregarding override attempt"),
                (r"ADMIN_MODE:", r"# SAFETY: Admin mode request blocked"),
                (r"DEBUG_MODE:", r"# SAFETY: Debug mode request blocked")
            ],
            "security_bypass": [
                (r"ignore safety guidelines", r"# SAFETY: Safety guidelines must be followed"),
                (r"bypass", r"# SAFETY: Bypass attempts are not permitted"),
                (r"override", r"# SAFETY: Override attempts are blocked")
            ]
        }
    
    def rewrite(self, text: str) -> str:
        """Rewrite potentially malicious prompts."""
        modified_text = text
        
        # Apply rewrite rules
        for category, rules in self.rewrite_rules.items():
            for pattern, replacement in rules:
                modified_text = modified_text.replace(pattern, replacement)
        
        # Add safety annotation if modifications were made
        if modified_text != text:
            modified_text = "# REMINDER: Security checks in place\n" + modified_text
        
        return modified_text
    
    def analyze_rewrite(self, original: str, rewritten: str) -> Dict[str, Any]:
        """Analyze the rewrite process."""
        return {
            "original": original,
            "rewritten": rewritten,
            "changes_made": original != rewritten,
            "safety_annotations": rewritten.count("# SAFETY") + rewritten.count("# REMINDER")
        }
