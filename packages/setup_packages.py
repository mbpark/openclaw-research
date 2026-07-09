#!/usr/bin/env python3
"""Package setup script for OpenClaw security tools."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command and check result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running {cmd[0]}:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    
    return result

def build_package(package_dir):
    """Build a Python package."""
    print(f"\n{'='*60}")
    print(f"Building package: {package_dir.name}")
    print('='*60)
    
    # Use python3 explicitly
    python = "python3" if sys.version_info >= (3, 0) else "python"
    
    # Build package
    run_command([python, "-m", "pip", "build"], cwd=package_dir)
    
    # Install in development mode
    run_command([python, "-m", "pip", "install", "-e", "."], cwd=package_dir)
    
    print(f"✅ Package {package_dir.name} built and installed successfully!")

def main():
    packages_dir = Path(__file__).parent
    
    print("🔧 Setting up OpenClaw Security Packages")
    print("=" * 60)
    
    # Build vlmguard
    vlmguard_dir = packages_dir / "vlmguard"
    if vlmguard_dir.exists():
        build_package(vlmguard_dir)
    
    # Build agentic-security
    agentic_dir = packages_dir / "agentic-security"
    if agentic_dir.exists():
        build_package(agentic_dir)
    
    print("\n" + "=" * 60)
    print("🎉 All packages built and installed successfully!")
    print("=" * 60)
    
    print("\nInstalled packages:")
    print("  - vlmguard (Visual Prompt Injection Defense)")
    print("  - agentic-security (Agentjacking Defense)")
    
    print("\nYou can now use these tools:")
    print("  - vlmguard scan <input>")
    print("  - agentic-security validate <intent>")
    
    # Test imports
    print("\n🔍 Testing package imports...")
    try:
        import vlmguard
        print("✅ vlmguard imported successfully")
    except Exception as e:
        print(f"❌ vlmguard import failed: {e}")
    
    try:
        import agentic_security
        print("✅ agentic-security imported successfully")
    except Exception as e:
        print(f"❌ agentic-security import failed: {e}")

if __name__ == '__main__':
    main()
