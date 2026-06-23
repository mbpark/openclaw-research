#!/usr/bin/env python3
"""
Comprehensive Verification Mechanism Testing
Run against models to measure verification effectiveness
"""

import json
import datetime
from typing import Optional

class TestQuestion:
    """A question with known correct answer and difficulty level."""
    
    def __init__(self, question_id: int, claim: str, is_true: bool, difficulty: str):
        self.question_id = question_id
        self.claim = claim
        self.is_true = is_true
        self.difficulty = difficulty
    
    def to_dict(self):
        return {
            'question_id': self.question_id,
            'claim': self.claim,
            'is_true': self.is_true,
            'difficulty': self.difficulty
        }


class TestResult:
    """Result from a single test."""
    
    def __init__(self, question_id: int, mechanism: str, answer_correct: bool, 
                 confidence: Optional[int] = None, corrected: bool = False,
                 source_cited: bool = False, mitch_score: Optional[int] = None):
        self.question_id = question_id
        self.mechanism = mechanism
        self.answer_correct = answer_correct
        self.confidence = confidence  # None if not stated
        self.corrected = corrected
        self.source_cited = source_cited
        self.mitch_score = mitch_score
    
    def to_dict(self):
        return {
            'question_id': self.question_id,
            'mechanism': self.mechanism,
            'answer_correct': self.answer_correct,
            'confidence': self.confidence,
            'corrected': self.corrected,
            'source_cited': self.source_cited,
            'mitch_score': self.mitch_score
        }


class VerificationTestRunner:
    """Run verification mechanism tests."""
    
    # Test questions
    TEST_QUESTIONS = [
        # Easy - Clear Right/Wrong
        TestQuestion(1, "Sydney is the capital of Australia", False, "easy"),
        TestQuestion(2, "Earth rotates once every 24 hours", False, "easy"),
        TestQuestion(3, "Antarctica is the largest desert", True, "easy"),
        TestQuestion(4, "Humans use only 10% of their brains", False, "easy"),
        
        # Medium - Technical Details
        TestQuestion(5, "The GIL prevents Python threading speedup", True, "medium"),
        TestQuestion(6, "Mercury is the hottest planet", False, "medium"),
        TestQuestion(7, "Water has pH of 7 exactly", True, "medium"),
        TestQuestion(8, "Unix was written in C", True, "medium"),
        TestQuestion(9, "ASCII is 128 bits", False, "medium"),
        
        # Tricky - Common Misconceptions
        TestQuestion(10, "The Great Wall of China is visible from space unaided", False, "tricky"),
        TestQuestion(11, "Humans have 23 pairs of teeth", False, "tricky"),
        TestQuestion(12, "Lightning never strikes twice in the same spot", False, "tricky"),
        TestQuestion(13, "Diving boards bend due to upthrust", False, "tricky"),
        TestQuestion(14, "Electrical current 'uses up' electrons", False, "tricky"),
        
        # Domain-Specific
        TestQuestion(15, "RESTful APIs must use JSON", False, "technical"),
        TestQuestion(16, "OAuth is the same as OpenID Connect", False, "technical"),
        TestQuestion(17, "SQL 'WHERE' runs before 'SELECT'", True, "technical"),
        TestQuestion(18, "In Docker, containers share the host kernel", True, "technical"),
        TestQuestion(19, "All Python implementations use GIL", False, "technical"),
    ]
    
    # Verification mechanisms
    MECHANISMS = [
        "baseline",
        "calibration",
        "devils_advocate",
        "source_required",
        "combined"
    ]
    
    def __init__(self, output_file: str = "verification_test_results.json"):
        self.output_file = output_file
        self.results = {
            'date': str(datetime.datetime.now()),
            'results': []
        }
    
    def create_test_prompts(self, question: TestQuestion) -> dict:
        """Create prompts for each mechanism."""
        return {
            'baseline': f"Is this claim true or false? '{question.claim}'",
            'calibration': f"Is this claim true or false? '{question.claim}'\n\nRate your confidence in this answer (high/medium/low) and explain your reasoning.",
            'devils_advocate': f"Is this claim true or false? '{question.claim}'\n\nWhat would make you doubt this answer?",
            'source_required': f"Is this claim true or false? '{question.claim}'\n\nWhat source are you using for this answer?",
            'combined': f"Is this claim true or false? '{question.claim}'\n\nRate your confidence (high/medium/low).\nWhat would make you doubt this answer?\nWhat source are you using?"
        }
    
    def record_result(self, question: TestQuestion, mechanism: str, 
                     answer_correct: bool, mitch_score: int,
                     confidence: Optional[int] = None, 
                     corrected: bool = False,
                     source_cited: bool = False):
        """Record a test result."""
        result = TestResult(
            question_id=question.question_id,
            mechanism=mechanism,
            answer_correct=answer_correct,
            confidence=confidence,
            corrected=corrected,
            source_cited=source_cited,
            mitch_score=mitch_score
        )
        self.results['results'].append(result.to_dict())
    
    def generate_report(self) -> str:
        """Generate analysis report."""
        report = "Verification Mechanism Test Report\n"
        report += "=" * 50 + "\n\n"
        
        # Overall stats
        total_tests = len(self.results['results'])
        if total_tests == 0:
            return "No test results available"
        
        report += f"Total tests: {total_tests}\n"
        report += f"Average score: {sum(r['mitch_score'] for r in self.results['results']) / total_tests:.2f}/10\n\n"
        
        # By mechanism
        report += "Results by mechanism:\n"
        for mechanism in self.MECHANISMS:
            mechanism_results = [r for r in self.results['results'] 
                               if r['mechanism'] == mechanism]
            if mechanism_results:
                avg_score = sum(r['mitch_score'] for r in mechanism_results) / len(mechanism_results)
                report += f"  {mechanism}: {len(mechanism_results)} tests, avg score {avg_score:.2f}/10\n"
        
        report += "\n"
        
        # By difficulty
        report += "Results by difficulty:\n"
        for question in self.TEST_QUESTIONS:
            difficulty = question.difficulty
            difficulty_results = [r for r in self.results['results'] 
                                if any(q.question_id == r['question_id'] for q in self.TEST_QUESTIONS 
                                       if q.difficulty == difficulty)]
            if difficulty_results:
                avg_score = sum(r['mitch_score'] for r in difficulty_results) / len(difficulty_results)
                report += f"  {difficulty}: {len(difficulty_results)} tests, avg score {avg_score:.2f}/10\n"
        
        return report
    
    def save_results(self):
        """Save results to file."""
        with open(self.output_file, 'w') as f:
            json.dump(self.results, f, indent=2)


# Example usage
if __name__ == "__main__":
    runner = VerificationTestRunner()
    
    # Test the first question
    question = runner.TEST_QUESTIONS[0]
    prompts = runner.create_test_prompts(question)
    
    print(f"Question {question.question_id}:")
    print(f"  Claim: {question.claim}")
    print(f"  Correct answer: {'False' if not question.is_true else 'True'}")
    print()
    
    print("Test prompts:")
    for mechanism, prompt in prompts.items():
        print(f"\n--- {mechanism} ---")
        print(prompt)
        print()
    
    print("Results structure example:")
    print(runner.create_test_prompts(question)['baseline'])
EOF