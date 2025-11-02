#!/usr/bin/env python3
"""
Script de testare pentru Multi-Provider LLM support.
Testează fiecare provider disponibil pentru a verifica că funcționează corect.
"""

import os
import sys
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.llm_providers import LLMFactory
from tradingagents.dataflows.config import get_api_key


def test_provider(provider_name: str, model: str, test_message: str = "What is 2+2? Reply briefly.") -> Dict:
    """Testează un provider cu un model specific."""
    print(f"\n{'='*60}")
    print(f"Testing: {provider_name} / {model}")
    print(f"{'='*60}")
    
    try:
        # Create LLM instance
        llm = LLMFactory.create_llm(model, provider=provider_name)
        
        # Test invoke
        response = llm.invoke(test_message)
        
        print(f"✅ SUCCESS")
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Response: {response.content[:200]}...")
        if response.usage:
            print(f"Usage: {response.usage}")
        
        return {
            "status": "success",
            "provider": response.provider,
            "model": response.model,
            "content": response.content,
            "usage": response.usage
        }
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "provider": provider_name,
            "model": model
        }


def test_all_providers():
    """Testează toți providerii disponibili."""
    print("\n" + "="*60)
    print("Multi-Provider LLM Test Suite")
    print("="*60)
    
    # Get available providers
    providers = LLMFactory.list_providers()
    print(f"\nAvailable providers: {providers}")
    
    results = {}
    
    # Test OpenAI
    if "openai" in providers:
        api_key = get_api_key("openai_api_key", "OPENAI_API_KEY")
        if api_key:
            results["openai"] = test_provider("openai", "gpt-4o-mini")
        else:
            print("\n⚠️  OpenAI API key not found - skipping OpenAI test")
            results["openai"] = {"status": "skipped", "reason": "No API key"}
    
    # Test DeepSeek
    if "deepseek" in providers:
        api_key = get_api_key("deepseek_api_key", "DEEPSEEK_API_KEY")
        if api_key:
            results["deepseek"] = test_provider("deepseek", "deepseek-chat")
        else:
            print("\n⚠️  DeepSeek API key not found - skipping DeepSeek test")
            results["deepseek"] = {"status": "skipped", "reason": "No API key"}
    
    # Test OpenRouter
    if "openrouter" in providers:
        api_key = get_api_key("openrouter_api_key", "OPENROUTER_API_KEY")
        if api_key:
            # Test with OpenAI model through OpenRouter
            results["openrouter_openai"] = test_provider(
                "openrouter", 
                "openai/gpt-4o-mini"
            )
            # Test with Claude through OpenRouter
            results["openrouter_claude"] = test_provider(
                "openrouter",
                "anthropic/claude-3.5-haiku"
            )
        else:
            print("\n⚠️  OpenRouter API key not found - skipping OpenRouter test")
            results["openrouter"] = {"status": "skipped", "reason": "No API key"}
    
    # Test Anthropic (if available)
    if "anthropic" in providers:
        api_key = get_api_key("anthropic_api_key", "ANTHROPIC_API_KEY")
        if api_key:
            results["anthropic"] = test_provider("anthropic", "claude-3-5-haiku-20241022")
        else:
            print("\n⚠️  Anthropic API key not found - skipping Anthropic test")
            results["anthropic"] = {"status": "skipped", "reason": "No API key"}
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    failed_count = sum(1 for r in results.values() if r.get("status") == "failed")
    skipped_count = sum(1 for r in results.values() if r.get("status") == "skipped")
    
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⚠️  Skipped: {skipped_count}")
    
    return results


def test_factory_features():
    """Testează funcționalitățile factory-ului."""
    print("\n" + "="*60)
    print("Testing LLMFactory Features")
    print("="*60)
    
    # Test list providers
    print("\n1. Listing providers:")
    providers = LLMFactory.list_providers()
    for provider in providers:
        print(f"   - {provider}")
    
    # Test get available models
    print("\n2. Available models per provider:")
    for provider in providers:
        models = LLMFactory.get_available_models(provider)
        print(f"   {provider}: {len(models)} models")
        if models:
            print(f"      Examples: {', '.join(models[:3])}")
    
    # Test get default models
    print("\n3. Default models per provider:")
    for provider in providers:
        defaults = LLMFactory.get_default_models(provider)
        if defaults:
            print(f"   {provider}:")
            for key, model in defaults.items():
                print(f"      {key}: {model}")


if __name__ == "__main__":
    print("\n🚀 Starting Multi-Provider LLM Tests...\n")
    
    # Test factory features
    test_factory_features()
    
    # Test all providers
    results = test_all_providers()
    
    # Exit code based on results
    if any(r.get("status") == "success" for r in results.values()):
        print("\n✅ At least one provider works! You can proceed with deployment.")
        sys.exit(0)
    else:
        print("\n⚠️  No providers tested successfully. Check your API keys.")
        sys.exit(1)

