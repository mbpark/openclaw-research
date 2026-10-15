#!/usr/bin/env python3
"""
Setup script for The Field Agent Protocol
"""

import sys
import os
from pathlib import Path

def main():
    print("🔧 Setting up Field Agent Protocol package...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)
    
    # Install dependencies
    print("📦 Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -q cryptography pyyaml python-dotenv")
    
    # Install package in editable mode
    print("🔨 Installing package in editable mode...")
    os.system(f"{sys.executable} -m pip install -e .")
    
    print("\n✅ Installation complete!")
    print("\n🚀 Use the CLI commands:")
    print("  tfap init            - Initialize field network")
    print("  tfap discover        - Discover agents")
    print("  tfap setup           - Setup new agent")
    print("  tfap identity        - Show agent identity")
    print("\n📚 Read the documentation:")
    print("  https://github.com/mbpark/openclaw-research/tree/main/field-agent-protocol")

if __name__ == "__main__":
    main()
