#!/usr/bin/env python3
"""
Move expanded content from start of file to after Phase 3 section header
"""

def main():
    filepath = "/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v5_unified.md"
    
    with open(filepath, "r") as f:
        content = f.read()
    
    # Find the expanded content section (after line 3, the title)
    start_marker = "## Expanded Phase 3: Advanced Security Research"
    end_marker = "## Advanced Security Research — Phase 3"
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos > 0 and end_pos > start_pos:
        # Extract expanded content
        expanded = content[start_pos:end_pos]
        
        # Remove from original location
        content = content[:start_pos] + content[end_pos:]
        
        # Find Phase 3 header and insert after it
        phase3_pos = content.find(end_marker)
        # Find the next line after this header
        next_line = content.find('\n', phase3_pos) + 1
        
        # Insert expanded content there
        content = content[:next_line] + expanded + content[next_line:]
        
        # Write back
        with open(filepath, "w") as f:
            f.write(content)
        
        print("Moved expanded content successfully!")
    else:
        print(f"Could not locate content. start={start_pos}, end={end_pos}")

if __name__ == "__main__":
    main()
