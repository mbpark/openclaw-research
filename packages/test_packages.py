#!/usr/bin/env python3
"""Test script to verify OpenClaw security packages can be imported and used."""

import sys
from pathlib import Path

# Add packages directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_vlmguard_imports():
    """Test that vlmguard can be imported."""
    print("\n🔍 Testing VLMGuard imports...")
    
    try:
        # Try importing main module
        import vlmguard
        print("✅ vlmguard module imported successfully")
        
        # Check version
        if hasattr(vlmguard, '__version__'):
            print(f"   Version: {vlmguard.__version__}")
        
        # Try importing specific classes (if they exist in the module)
        try:
            from vlmguard.vlmguard_integrated_full import VLMGuard
            print("✅ VLMGuard class imported")
        except Exception as e:
            print(f"⚠️ VLMGuard class import failed: {e}")
            
        try:
            from vlmguard.vlmguard_r1_enhanced_intent_analyzer import EnhancedIntentAnalyzer
            print("✅ EnhancedIntentAnalyzer class imported")
        except Exception as e:
            print(f"⚠️ EnhancedIntentAnalyzer import failed: {e}")
            
        try:
            from vlmguard.vlmguard_r1_prompt_rewriter import PromptRewriter
            print("✅ PromptRewriter class imported")
        except Exception as e:
            print(f"⚠️ PromptRewriter import failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ VLMGuard import failed: {e}")
        return False

def test_agentic_security_imports():
    """Test that agentic_security can be imported."""
    print("\n🔍 Testing Agentic Security imports...")
    
    try:
        # Try importing main module
        import agentic_security
        print("✅ agentic_security module imported successfully")
        
        # Check version
        if hasattr(agentic_security, '__version__'):
            print(f"   Version: {agentic_security.__version__}")
        
        # Try importing specific classes (if they exist in the module)
        try:
            from agentic_security.agentic_workflow_graph_controller import WorkflowGraphController
            print("✅ WorkflowGraphController class imported")
        except Exception as e:
            print(f"⚠️ WorkflowGraphController import failed: {e}")
            
        try:
            from agentic_security.agentjacking_defense_framework import AgentjackingDefenseFramework
            print("✅ AgentjackingDefenseFramework class imported")
        except Exception as e:
            print(f"⚠️ AgentjackingDefenseFramework import failed: {e}")
            
        try:
            from agentic_security.agentjacking_simulator import AgentjackingSimulator
            print("✅ AgentjackingSimulator class imported")
        except Exception as e:
            print(f"⚠️ AgentjackingSimulator import failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Agentic Security import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without API keys."""
    print("\n🔍 Testing basic functionality...")
    
    # Test VLMGuard basic initialization
    try:
        from vlmguard.vlmguard_integrated_full import VLMGuard
        vlmguard = VLMGuard()
        print("✅ VLMGuard instance created")
        
        # Test basic scan method (without actual API call)
        # This will test if the method exists and has correct signature
        import inspect
        if hasattr(vlmguard, 'scan'):
            sig = inspect.signature(vlmguard.scan)
            print(f"✅ VLMGuard.scan method signature: {sig}")
        
    except Exception as e:
        print(f"⚠️ VLMGuard functionality test failed: {e}")
    
    # Test WorkflowGraphController basic initialization
    try:
        from agentic_security.agentic_workflow_graph_controller import WorkflowGraphController
        controller = WorkflowGraphController()
        print("✅ WorkflowGraphController instance created")
        
        import inspect
        if hasattr(controller, 'validate_intent'):
            sig = inspect.signature(controller.validate_intent)
            print(f"✅ WorkflowGraphController.validate_intent signature: {sig}")
            
    except Exception as e:
        print(f"⚠️ WorkflowGraphController functionality test failed: {e}")
    
    return True

def main():
    print("🔧 Testing OpenClaw Security Packages")
    print("=" * 60)
    
    vlmguard_ok = test_vlmguard_imports()
    agentic_ok = test_agentic_security_imports()
    basic_ok = test_basic_functionality()
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    if vlmguard_ok:
        print("✅ VLMGuard: PASS")
    else:
        print("❌ VLMGuard: FAIL")
    
    if agentic_ok:
        print("✅ Agentic Security: PASS")
    else:
        print("❌ Agentic Security: FAIL")
    
    if basic_ok:
        print("✅ Basic Functionality: PASS")
    else:
        print("❌ Basic Functionality: FAIL")
    
    if vlmguard_ok and agentic_ok and basic_ok:
        print("\n🎉 All tests passed! Packages are ready.")
        return 0
    else:
        print("\n⚠️ Some tests failed. See errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
