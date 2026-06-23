#!/usr/bin/env python3
"""
Move metadata block from line ~957 to after title (line 3)
"""

def main():
    filepath = "/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v5_unified.md"
    
    with open(filepath, "r") as f:
        content = f.read()
    
    # Find and extract the metadata block
    meta_start = content.find("**Date:** June 6")
    meta_end = content.find("\n---\n\n## Appendices")
    
    if meta_start > 0 and meta_end > 0:
        meta_block = content[meta_start:meta_end]
        print(f"Found metadata block: {len(meta_block)} chars")
        
        # Remove from current location
        content = content[:meta_start] + "\n---\n\n## Appendices" + content[meta_end:]
        print("Removed metadata from current location")
        
        # Find where to insert (after title)
        insert_pos = content.find("# Version 5 — With Advanced Security Research (Phase 3)")
        # Insert right after the title
        insert_pos += len("# Version 5 — With Advanced Security Research (Phase 3)")
        content = content[:insert_pos] + "\n\n" + meta_block + "\n" + content[insert_pos:]
        print("Inserted metadata after title")
        
        # Write back
        with open(filepath, "w") as f:
            f.write(content)
        
        print("Done!")
    else:
        print(f"Could not locate metadata. start={meta_start}, end={meta_end}")

if __name__ == "__main__":
    main()
