#!/usr/bin/env python3
"""
Fix duplicate Appendices section
"""

def main():
    filepath = "/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v5_unified.md"
    
    with open(filepath, "r") as f:
        content = f.read()
    
    # Find the duplicate pattern and remove it
    # The pattern is "---\n\n## Appendices\n---\n\n## Appendices"
    # Replace with "---\n\n## Appendices"
    
    old_pattern = """---

## Appendices
---

## Appendices"""
    
    new_pattern = """---

## Appendices"""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed duplicate Appendices")
        
        with open(filepath, "w") as f:
            f.write(content)
    else:
        print("Could not find duplicate pattern")

if __name__ == "__main__":
    main()
