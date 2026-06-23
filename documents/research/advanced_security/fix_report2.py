#!/usr/bin/env python3
"""
Fix: Remove Phase 3 content from after title and insert before Appendices
"""

def main():
    filepath = "/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v5_unified.md"
    
    with open(filepath, "r") as f:
        content = f.read()
    
    # Find the start and end of Phase 3 content
    start_marker = "## Advanced Security Research — Phase 3"
    end_marker = "## Table of Contents"
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    print(f"Found start at position {start_pos}")
    print(f"Found end at position {end_pos}")
    
    if start_pos > 0 and end_pos > start_pos:
        # Extract Phase 3 content
        phase3_content = content[start_pos:end_pos]
        print(f"Phase 3 content length: {len(phase3_content)} chars")
        
        # Remove from current location
        content = content[:start_pos] + content[end_pos:]
        print("Removed Phase 3 content from current location")
        
        # Find where to insert it (before Appendices)
        appendices_pos = content.find("## Appendices")
        print(f"Appendices at position {appendices_pos}")
        
        if appendices_pos > 0:
            # Insert Phase 3 content right before Appendices
            content = content[:appendices_pos] + phase3_content + content[appendices_pos:]
            print("Inserted Phase 3 content before Appendices")
        else:
            print("ERROR: Could not find Appendices section")
            return
        
        # Write back
        with open(filepath, "w") as f:
            f.write(content)
        
        print("Done!")
    else:
        print("Could not locate content")

if __name__ == "__main__":
    main()
