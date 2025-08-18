#!/usr/bin/env python3
"""
Test file for prompt configuration system.
This tests the new centralized prompt management approach.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.prompt_config import (
    get_rag_system_prompt, 
    get_rag_user_prompt, 
    format_prompt,
    LANGUAGE_CONFIG
)

def test_language_config():
    """Test language configuration."""
    print("Testing language configuration...")
    
    assert LANGUAGE_CONFIG["default"] == "español"
    assert "español" in LANGUAGE_CONFIG["supported"]
    assert "english" in LANGUAGE_CONFIG["supported"]
    assert LANGUAGE_CONFIG["fallback"] == "español"
    
    print("✅ Language configuration tests passed")

def test_system_prompts():
    """Test system prompt retrieval."""
    print("Testing system prompts...")
    
    # Test Spanish prompt
    spanish_prompt = get_rag_system_prompt("español")
    assert "español" in spanish_prompt
    assert "SIEMPRE DA LA RESPUESTA EN ESPAÑOL" in spanish_prompt
    
    # Test English prompt
    english_prompt = get_rag_system_prompt("english")
    assert "English" in english_prompt
    assert "ALWAYS GIVE THE ANSWER IN ENGLISH" in english_prompt
    
    # Test default language
    default_prompt = get_rag_system_prompt()
    assert default_prompt == spanish_prompt
    
    print("✅ System prompt tests passed")

def test_user_prompts():
    """Test user prompt retrieval and formatting."""
    print("Testing user prompts...")
    
    # Test Spanish prompt
    spanish_template = get_rag_user_prompt("español")
    assert "{context}" in spanish_template
    assert "{question}" in spanish_template
    
    # Test English prompt
    english_template = get_rag_user_prompt("english")
    assert "{context}" in english_template
    assert "{question}" in english_template
    
    # Test prompt formatting
    formatted_prompt = format_prompt(spanish_template, context="Test context", question="Test question")
    assert "Test context" in formatted_prompt
    assert "Test question" in formatted_prompt
    assert "{context}" not in formatted_prompt
    assert "{question}" not in formatted_prompt
    
    print("✅ User prompt tests passed")

def test_error_handling():
    """Test error handling for invalid inputs."""
    print("Testing error handling...")
    
    try:
        get_rag_system_prompt("invalid_language")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        format_prompt("Template with {missing_variable}", context="test")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✅ Error handling tests passed")

def main():
    """Run all tests."""
    print("🧪 Running prompt configuration tests...\n")
    
    try:
        test_language_config()
        test_system_prompts()
        test_user_prompts()
        test_error_handling()
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
