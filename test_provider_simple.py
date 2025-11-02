#!/usr/bin/env python3
"""
Script simplu de testare pentru un singur provider.
Folosește pentru testare rapidă înainte de deploy.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.llm_providers import LLMFactory


def main():
    """Test simplu - testează provider-ul din environment."""
    import os
    
    # Read provider and model from environment or use defaults
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("TEST_MODEL", "gpt-4o-mini")
    test_message = "Say 'Hello from Multi-Provider system!' and tell me what 2+2 equals."
    
    print(f"\n🧪 Testing Provider: {provider}")
    print(f"📦 Model: {model}")
    print(f"💬 Test message: {test_message}\n")
    
    try:
        # Create LLM
        print(f"Creating LLM instance...")
        llm = LLMFactory.create_llm(model, provider=provider)
        
        # Test invoke
        print(f"Invoking LLM...")
        response = llm.invoke(test_message)
        
        print(f"\n✅ SUCCESS!")
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"\nResponse:\n{response.content}")
        
        if response.usage:
            print(f"\nToken usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

