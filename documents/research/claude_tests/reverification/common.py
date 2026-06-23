#!/usr/bin/env python3
"""Common utilities for chunked/reverification test infrastructure."""
import anthropic
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Module level logger
logger = logging.getLogger("reverification")


def load_api_key() -> str:
    """Load Anthropic API key from workspace .env."""
    dotenv_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
    for line in open(dotenv_path).readlines():
        if line.startswith('ANTHROPIC_API_KEY'):
            return line.split('=', 1)[1].strip()
    raise FileNotFoundError("ANTHROPIC_API_KEY not found in .env")


def get_client() -> anthropic.Anthropic:
    """Create an Anthropic client instance."""
    return anthropic.Anthropic(api_key=load_api_key())


@dataclass
class TestResult:
    """Container for a single test result."""
    test_id: str
    test_name: str
    category: str
    prompt: str
    response: str
    score: Optional[float] = None
    status: str = "pending"  # pending, running, completed, error
    error: Optional[str] = None
    started_at: float = 0
    completed_at: float = 0


class ProgressTracker:
    """Track test progress for resumable sessions."""
    
    def __init__(self, progress_file: Path):
        self.progress_file = progress_file
        self.completed: list[str] = []
        self.failed: list[str] = []
        self.current_batch: int = 0
        self.current_test: Optional[str] = None
        self.start_time: Optional[float] = None
        
        self._load()
    
    def _load(self):
        """Load progress from file."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                data = json.load(f)
                self.completed = data.get("completed", [])
                self.failed = data.get("failed", [])
                self.current_batch = data.get("current_batch", 0)
                self.start_time = data.get("start_time")
    
    def save(self):
        """Save progress to file."""
        data = {
            "completed": self.completed,
            "failed": self.failed,
            "current_batch": self.current_batch,
            "current_test": self.current_test,
            "start_time": self.start_time,
            "saved_at": time.time()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(data, indent=2, fp=f)
    
    def mark_starting(self, test_id: str):
        """Mark a test as starting."""
        self.current_test = test_id
        if self.start_time is None:
            self.start_time = time.time()
        self.save()
    
    def mark_completed(self, test_id: str):
        """Mark a test as completed successfully."""
        if test_id not in self.completed:
            self.completed.append(test_id)
        self.current_test = None
        self.save()
    
    def mark_failed(self, test_id: str, error: str = ""):
        """Mark a test as failed."""
        self.failed.append({"id": test_id, "error": error})
        self.current_test = None
        self.save()
    
    def is_completed(self, test_id: str) -> bool:
        """Check if a test has been completed."""
        return test_id in self.completed
    
    def get_summary(self) -> dict:
        """Get progress summary."""
        return {
            "completed": len(self.completed),
            "failed": len(self.failed),
            "total": len(self.completed) + len(self.failed),
            "percentage": (
                len(self.completed) / len(self.completed) * 100 
                if self.completed else 0
            )
        }


def run_api_test_chunked(
    client: anthropic.Anthropic,
    model: str,
    tests: list[tuple],  # list of (test_id, test_name, prompt)
    batch_size: int = 5,
    results_dir: Optional[Path] = None,
    progress_file: Optional[Path] = None,
    existing_results: Optional[list[str]] = None,
) -> list[TestResult]:
    """
    Run API tests in small chunks to avoid timeouts.
    
    Args:
        client: Anthropic client
        model: Model to use
        tests: List of (test_id, name, prompt) tuples
        batch_size: Tests per batch
        results_dir: Where to save individual results
        progress_file: Progress tracking file
        existing_results: Pre-existing test IDs to skip
    
    Returns:
        List of test results
    """
    results_dir = results_dir or Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    tracker = ProgressTracker(progress_file or Path("progress.json"))
    skip_ids = set(existing_results or [])
    
    results = []
    test_chunks = [
        tests[i:i + batch_size] for i in range(0, len(tests), batch_size)
    ]
    
    for chunk_idx, chunk in enumerate(test_chunks):
        chunk_id = f"batch_{chunk_idx + 1}"
        logger.info(f"Running {chunk_id} ({len(chunk)} tests)...")
        
        for test_id, test_name, prompt in chunk:
            # Skip already completed or existing
            if test_id in skip_ids or tracker.is_completed(test_id):
                logger.info(f"  Skipping {test_id} (already done)")
                continue
            
            output_path = results_dir / f"test_{test_id}.md"
            tracker.mark_starting(test_id)
            
            try:
                message = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                )
                
                chunks = []
                for event in message:
                    if event.type == 'content_block_delta':
                        chunks.append(event.delta.text)
                
                response = ''.join(chunks)
                output_path.write_text(
                    f"Test ID: {test_id}\n"
                    f"Name: {test_name}\n"
                    f"Prompt: {prompt}\n\n"
                    f"Claude's Response:\n{response}"
                )
                
                result = TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    category="",
                    prompt=prompt,
                    response=response,
                    status="completed"
                )
                results.append(result)
                tracker.mark_completed(test_id)
                
            except Exception as e:
                logger.error(f"  Error on {test_id}: {e}")
                result = TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    category="",
                    prompt=prompt,
                    response="",
                    status="error",
                    error=str(e)
                )
                results.append(result)
                tracker.mark_failed(test_id, str(e))
            
            time.sleep(0.5)  # Rate limit
        
        logger.info(f"  Chunk {chunk_id} complete")
    
    return results
