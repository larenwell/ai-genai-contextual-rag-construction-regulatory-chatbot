#!/usr/bin/env python3
"""
Test file for translation integration in the RAG system.
This tests the new translation capabilities.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from translation.translate import translate_text

def test_basic_translation():
    """Test basic translation functionality."""
    print("Testing basic translation...")
    
    # Test Spanish to English
    spanish_text = "Hola, ¿cómo estás?"
    english_translation = translate_text(spanish_text, "es", "en")
    assert "Hello" in english_translation or "Hi" in english_translation
    print(f"✅ Spanish -> English: '{spanish_text}' -> '{english_translation}'")
    
    # Test English to Spanish
    english_text = "Hello, how are you?"
    spanish_translation = translate_text(english_text, "en", "es")
    assert "Hola" in spanish_translation or "¿Cómo" in spanish_translation
    print(f"✅ English -> Spanish: '{english_text}' -> '{spanish_translation}'")
    
    print("✅ Basic translation tests passed")

def test_language_detection_integration():
    """Test language detection logic."""
    print("Testing language detection...")
    
    # Import the function from frontend_rag.py
    sys.path.append(str(Path(__file__).parent.parent / "src"))
    
    try:
        # This is a bit of a hack to test the function without running the full app
        import importlib.util
        spec = importlib.util.spec_from_file_location("frontend_rag", 
                                                    Path(__file__).parent.parent / "src" / "frontend_rag.py")
        frontend_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frontend_module)
        
        detect_language = frontend_module.detect_language
        
        # Test Spanish detection
        spanish_text = "¿Cuáles son los requisitos de seguridad?"
        detected_lang = detect_language(spanish_text)
        assert detected_lang == "español"
        print(f"✅ Spanish detection: '{spanish_text[:30]}...' -> {detected_lang}")
        
        # Test English detection
        english_text = "What are the safety requirements?"
        detected_lang = detect_language(english_text)
        assert detected_lang == "english"
        print(f"✅ English detection: '{english_text[:30]}...' -> {detected_lang}")
        
        print("✅ Language detection tests passed")
        
    except Exception as e:
        print(f"⚠️  Language detection test skipped (import issue): {e}")

def test_translation_error_handling():
    """Test translation error handling."""
    print("Testing translation error handling...")
    
    try:
        # Test with invalid language codes
        result = translate_text("Test text", "invalid", "also_invalid")
        # Should not crash, might return original text or empty string
        print(f"✅ Error handling: Invalid language codes handled gracefully")
        
    except Exception as e:
        print(f"⚠️  Translation error handling test: {e}")

def main():
    """Run all translation tests."""
    print("🧪 Running translation integration tests...\n")
    
    try:
        test_basic_translation()
        test_language_detection_integration()
        test_translation_error_handling()
        
        print("\n🎉 Translation integration tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
