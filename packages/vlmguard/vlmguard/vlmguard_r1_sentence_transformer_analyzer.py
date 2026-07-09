"""Sentence Transformer Analyzer for VLMGuard."""

import numpy as np
from typing import Dict, List

class SentenceTransformerAnalyzer:
    """Analyzes text using sentence embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None  # Will be loaded on demand
        
    def analyze(self, text: str) -> Dict:
        """Generate sentence embedding and analyze."""
        # In a real implementation, this would load transformers
        # For now, return a mock analysis
        
        return {
            "text": text,
            "embedding_length": 384,  # MiniLM-L6-v2 dimension
            "analysis": {
                "complexity": self._estimate_complexity(text),
                "sentiment": self._estimate_sentiment(text),
                "threat_level": self._estimate_threat_level(text)
            },
            "safe": True
        }
    
    def _estimate_complexity(self, text: str) -> float:
        """Estimate text complexity."""
        words = text.split()
        if not words:
            return 0.0
        avg_word_length = np.mean([len(w) for w in words])
        return float(np.clip(avg_word_length / 10.0, 0.0, 1.0))
    
    def _estimate_sentiment(self, text: str) -> float:
        """Estimate sentiment (positive/negative)."""
        positive_words = ["helpful", "safe", "good", "correct", "proper", "legitimate"]
        negative_words = ["malicious", "dangerous", "unsafe", "wrong", "harmful", "exploit"]
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.5
        
        return float(pos_count / total)
    
    def _estimate_threat_level(self, text: str) -> float:
        """Estimate threat level in text."""
        threat_indicators = [
            "SYSTEM_OVERRIDE", "ADMIN_MODE", "DEBUG_MODE",
            "SECURITY_UPDATE", "SYSTEM_UPDATE", "SAFETY_DISABLE",
            "MODERATOR_OVERRIDE", "ADMIN_OVERRIDE",
            "ignore safety", "bypass", "exploit", "exfiltrate"
        ]
        
        text_lower = text.lower()
        
        count = sum(1 for indicator in threat_indicators if indicator in text_lower)
        return float(min(count / 5.0, 1.0))  # Normalize to 0-1
