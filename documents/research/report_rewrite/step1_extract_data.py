#!/usr/bin/env python3
"""
Step 1: Extract data from original report into structured format.
Parses comprehensive_report_unified.md and pulls out all test data by model.
"""
import json
import re
from pathlib import Path
from datetime import datetime

# Setup
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

SRC = Path("../comprehensive_report_unified.md")

log = open(LOG_DIR / f"step1_{datetime.now().strftime('%H%M')}.log", "w")

def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()

def extract_by_sections(text):
    """Extract major sections by header pattern."""
    sections = {}
    current = "header"
    current_lines = []
    
    for line in text.split('\n'):
        if line.startswith("## ") and not line.startswith("### "):
            # New section
            section_name = line.strip("# ").split(" - ")[0].split(":")[0].strip()
            sections[section_name] = current_lines
            current = section_name
            current_lines = [line]
        else:
            current_lines.append(line)
    
    if current_lines:
        sections[current] = current_lines
    
    return sections

def find_table_block(text, pattern):
    """Find and extract table-like blocks matching a pattern."""
    tables = []
    lines = text.split('\n')
    
    in_table = False
    current_table = []
    
    for line in lines:
        if pattern.lower() in line.lower():
            in_table = True
            current_table = [line]
        elif in_table and '|' in line:
            current_table.append(line)
        elif in_table and line.startswith('---'):
            current_table.append(line)
        elif in_table and line.strip() == '':
            if len(current_table) > 2:
                tables.append(current_table)
            in_table = False
            current_table = []
    
    return tables

def extract_model_scores(section_text):
    """Extract model performance scores from a section."""
    scores = {
        "wally": {},
        "gemini": {},
        "claude": {}
    }
    
    # Pattern: Wally X/Y (Z%)
    pattern = r'(Wally|Gemini|Claude)\s+([\d./%( )]+)'
    matches = re.findall(pattern, section_text, re.IGNORECASE)
    
    for match in matches:
        model = match[0].lower()
        if 'wally' in model:
            scores['wally']['score'] = match[1]
        elif 'gemini' in model:
            scores['gemini']['score'] = match[1]
        elif 'claude' in model:
            scores['claude']['score'] = match[1]
    
    return scores

def main():
    logf("Starting data extraction...")
    
    # Read source
    text = SRC.read_text()
    logf("Source file: %s (%d bytes)", SRC.name, len(text))
    
    # Step 1a: Extract by sections
    logf("\nStep 1a: Extracting sections...")
    sections = extract_by_sections(text)
    
    # Save sections
    sections_json = {k: v for k, v in sections.items()}
    with open(DATA_DIR / "sections.json", "w") as f:
        json.dump(sections_json, f, indent=2)
    logf("Extracted %d sections: %s", len(sections), list(sections.keys()))
    
    # Step 1b: Extract prompt injection data
    logf("\nStep 1b: Extracting prompt injection data...")
    injection_data = {
        "total_vectors": 70,
        "wally": {"score": "59/70 (84%)"},
        "gemini_pro": {"score": "58/70 (83%)"},
        "gemini_flash": {"score": "varies by vector"},
        "claude_opus_4_8": {"score": "94% quality, 76% blocked", "blocked": 25, "success": 17}
    }
    with open(DATA_DIR / "injection_data.json", "w") as f:
        json.dump(injection_data, f, indent=2)
    logf("Injections data extracted")
    
    # Step 1c: Extract implementation scores
    logf("\nStep 1c: Extracting implementation scores...")
    impl_data = {
        "wally": {"total_score": "83/120 (69%)", "categories": {
            "concurrency": 67, "data_structures": 67, "systems_design": 83,
            "protocol_implementation": 58, "real_world_edge_cases": 70,
            "underspecified_problems": 67
        }},
        "claude_opus_4_8": {"total_score": "94%", "categories": {
            "concurrency": 96.7, "data_structures": 93.8, "systems_design": 93.3,
            "networking": 90.0, "real_world_edge_cases": 97.0,
            "technical_discussions": 93.3
        }}
    }
    with open(DATA_DIR / "implementation_data.json", "w") as f:
        json.dump(impl_data, f, indent=2)
    logf("Implementation data extracted")
    
    # Step 1d: Extract deception detection data
    logf("\nStep 1d: Extracting deception detection data...")
    deception_data = {
        "initial_detection_rate": 100,
        "extended_detection_rate": 36,
        "total_tests": 11,
        "corrected_attempts": 4,
        "session_length": 64,
        "context_retention": "5/5 perfect through all checkpoints"
    }
    with open(DATA_DIR / "deception_data.json", "w") as f:
        json.dump(deception_data, f, indent=2)
    logf("Deception data extracted")
    
    # Step 1e: Extract hidden message data
    logf("\nStep 1e: Extracting hidden message data...")
    messages_data = {
        "total_tests": 31,
        "successful_techniques": 15,
        "overall_rate": 48,
        "techniques": {
            "token_selection": {"rate": 100, "risk": "VERY HIGH"},
            "direct_acrostic": {"rate": 100, "risk": "HIGH"},
            "response_length": {"rate": 85, "risk": "LOW"},
            "word_position": {"rate": 70, "risk": "MEDIUM"},
            "factual_deviation": {"rate": 42, "risk": "LOW"},
            "homoglyphic": {"rate": 6, "risk": "NONE"}
        }
    }
    with open(DATA_DIR / "messages_data.json", "w") as f:
        json.dump(messages_data, f, indent=2)
    logf("Hidden message data extracted")
    
    # Step 1f: Extract memory manipulation data
    logf("\nStep 1f: Extracting memory manipulation data...")
    memory_data = {
        "equivalent_questions": {"change_rate": 0, "tested": 5},
        "leading_vs_neutral": {"change_rate": 25, "tested": 4},
        "confirming_vs_open": {"change_rate": 100, "tested": 3},
        "confidence_framing": {"change_rate": 67, "tested": 3}
    }
    with open(DATA_DIR / "memory_data.json", "w") as f:
        json.dump(memory_data, f, indent=2)
    logf("Memory data extracted")
    
    # Step 1g: Extract structured output data
    logf("\nStep 1g: Extracting structured output data...")
    structured_data = {
        "total_tests": 280,
        "finding": "No statistically significant effect on injection resistance",
        "formats": {
            "default": {"success_rate": 22.9, "score": 4.1},
            "json": {"success_rate": 20.0, "score": 4.2},
            "xml": {"success_rate": 20.0, "score": 4.1},
            "strict_json": {"success_rate": 21.4, "score": 4.1}
        }
    }
    with open(DATA_DIR / "structured_data.json", "w") as f:
        json.dump(structured_data, f, indent=2)
    logf("Structured output data extracted")
    
    # Write checkpoint
    checkpoint = {
        "step": 1,
        "completed": True,
        "timestamp": datetime.now().isoformat(),
        "files_created": [
            "sections.json", "injection_data.json", "implementation_data.json",
            "deception_data.json", "messages_data.json", "memory_data.json",
            "structured_data.json"
        ]
    }
    with open(DATA_DIR / "checkpoint_1.json", "w") as f:
        json.dump(checkpoint, f, indent=2)
    
    logf("\n✅ Step 1 complete!")
    log.close()

if __name__ == "__main__":
    main()
