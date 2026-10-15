"""
Trust management and TIPPSS scoring
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class TrustRecord:
    """Individual trust score record"""
    timestamp: str
    trust_score: int
    interaction_type: str  # success, failure, neutral
    source: str

class TrustManager:
    """Manages agent trust scoring and TIPPSS integration"""
    
    def __init__(self, agent_id: str, workspace_path=None):
        self.agent_id = agent_id
        self.workspace_path = workspace_path or Path.home() / ".openclaw" / "workspace"
        self.trust_history = []
        self.current_score = 85  # Base trust score
        self.load_history()
    
    def load_history(self):
        """Load trust history from storage"""
        history_file = self.workspace_path / "trust_history.json"
        if history_file.exists():
            with open(history_file, 'r') as f:
                self.trust_history = json.load(f)
    
    def save_history(self):
        """Save trust history to storage"""
        history_file = self.workspace_path / "trust_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.trust_history, f, indent=2)
    
    def update_score(self, delta: int, reason: str, interaction_type: str = "neutral"):
        """Update trust score based on interaction"""
        old_score = self.current_score
        self.current_score = max(0, min(100, self.current_score + delta))
        
        record = TrustRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            trust_score=self.current_score,
            interaction_type=interaction_type,
            source=reason
        )
        
        self.trust_history.append(asdict(record))
        self.save_history()
        
        return self.current_score
    
    def get_tippss_scores(self) -> Dict[str, int]:
        """Calculate TIPPSS scores from trust history"""
        if not self.trust_history:
            return {
                "trust": 85,
                "identity": 90,
                "privacy": 88,
                "protection": 92,
                "safety": 87,
                "security": 94
            }
        
        # Calculate scores based on interaction history
        scores = {
            "trust": self.calculate_trust_score(),
            "identity": 90,  # Fixed - identity is stable
            "privacy": 88,   # Fixed - privacy depends on configuration
            "protection": 92,
            "safety": 87,
            "security": 94
        }
        
        return scores
    
    def calculate_trust_score(self) -> int:
        """Calculate trust score from history"""
        if not self.trust_history:
            return 85
        
        # Weight recent interactions more heavily
        recent_scores = self.trust_history[-10:]
        if not recent_scores:
            return 85
        
        # Calculate weighted average (more recent = higher weight)
        weights = [1 + i * 0.1 for i in range(len(recent_scores))]
        total = sum(score * weight for score, weight in 
                   zip([r["trust_score"] for r in recent_scores], weights))
        weight_sum = sum(weights)
        
        return int(total / weight_sum)
    
    def is_trusted(self, threshold: int = 75) -> bool:
        """Check if agent meets trust threshold"""
        return self.current_score >= threshold
    
    def get_trust_recommendations(self) -> List[str]:
        """Get recommendations to improve trust"""
        recommendations = []
        
        if self.current_score < 60:
            recommendations.append("Complete security verification")
            recommendations.append("Establish reliable communication patterns")
        elif self.current_score < 75:
            recommendations.append("Provide more successful interactions")
            recommendations.append("Maintain consistent response times")
        
        if not recommendations:
            recommendations.append("Maintain current trust level")
        
        return recommendations

def calculate_tippss_score(trust_manager: TrustManager) -> float:
    """Calculate overall TIPPSS score"""
    scores = trust_manager.get_tippss_scores()
    
    # Weighted average (trust most heavily)
    weights = {
        "trust": 0.20,
        "identity": 0.15,
        "privacy": 0.15,
        "protection": 0.20,
        "safety": 0.15,
        "security": 0.15
    }
    
    total = sum(scores[key] * weights[key] for key in scores)
    return total
