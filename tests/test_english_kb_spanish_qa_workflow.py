#!/usr/bin/env python3
"""
Test file for the optimized English KB + Spanish Q&A workflow.
This tests the specific use case where knowledge base is in English but Q&A should be in Spanish.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_workflow_optimization():
    """Test the workflow optimization logic."""
    print("Testing English KB + Spanish Q&A workflow optimization...")
    
    try:
        # Import the optimization function
        import importlib.util
        spec = importlib.util.spec_from_file_location("frontend_rag", 
                                                    Path(__file__).parent.parent / "src" / "frontend_rag.py")
        frontend_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frontend_module)
        
        optimize_workflow = frontend_module.optimize_for_english_kb_spanish_qa
        
        # Test Case 1: Spanish question
        print("\n📝 Test Case 1: Spanish question")
        spanish_question = "¿Cuáles son los requisitos de seguridad para equipos eléctricos?"
        search_query, context_lang, response_lang = optimize_workflow(spanish_question, "español")
        
        assert context_lang == "english", f"Expected 'english', got '{context_lang}'"
        assert response_lang == "español", f"Expected 'español', got '{response_lang}'"
        assert search_query != spanish_question, "Search query should be translated to English"
        print(f"✅ Spanish question -> English KB search -> Spanish response")
        print(f"   Original: {spanish_question}")
        print(f"   Search: {search_query}")
        
        # Test Case 2: English question
        print("\n📝 Test Case 2: English question")
        english_question = "What are the safety requirements for electrical equipment?"
        search_query, context_lang, response_lang = optimize_workflow(english_question, "english")
        
        assert context_lang == "english", f"Expected 'english', got '{context_lang}'"
        assert response_lang == "español", f"Expected 'español', got '{response_lang}'"
        assert search_query == english_question, "Search query should remain in English"
        print(f"✅ English question -> English KB search -> Spanish response")
        print(f"   Original: {english_question}")
        print(f"   Search: {search_query}")
        
        # Test Case 3: Mixed language question
        print("\n📝 Test Case 3: Mixed language question")
        mixed_question = "What are los requisitos for safety equipment?"
        search_query, context_lang, response_lang = optimize_workflow(mixed_question, "english")
        
        assert context_lang == "english", f"Expected 'english', got '{context_lang}'"
        assert response_lang == "español", f"Expected 'español', got '{response_lang}'"
        print(f"✅ Mixed question -> English KB search -> Spanish response")
        
        print("\n🎉 All workflow optimization tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_integration():
    """Test the translation integration for the workflow."""
    print("\nTesting translation integration...")
    
    try:
        from translation.translate import translate_text
        
        # Test English to Spanish translation (KB -> User)
        english_kb_content = "Safety requirements for electrical equipment include proper grounding, insulation, and protective devices."
        spanish_translation = translate_text(english_kb_content, "en", "es")
        
        assert "requisitos" in spanish_translation.lower() or "seguridad" in spanish_translation.lower()
        print(f"✅ English KB -> Spanish translation: '{english_kb_content[:50]}...' -> '{spanish_translation[:50]}...'")
        
        # Test Spanish to English translation (User -> KB search)
        spanish_question = "¿Cuáles son los requisitos de seguridad?"
        english_translation = translate_text(spanish_question, "es", "en")
        
        assert "safety" in english_translation.lower() or "requirements" in english_translation.lower()
        print(f"✅ Spanish question -> English search: '{spanish_question}' -> '{english_translation}'")
        
        print("✅ Translation integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Translation integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_language_detection():
    """Test language detection for the workflow."""
    print("\nTesting language detection...")
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("frontend_rag", 
                                                    Path(__file__).parent.parent / "src" / "frontend_rag.py")
        frontend_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frontend_module)
        
        detect_language = frontend_module.detect_language
        
        # Test Spanish detection
        spanish_texts = [
            "¿Cuáles son los requisitos?",
            "Necesito información sobre seguridad",
            "Los estándares de calidad son importantes"
        ]
        
        for text in spanish_texts:
            detected = detect_language(text)
            assert detected == "español", f"Expected 'español' for '{text}', got '{detected}'"
            print(f"✅ Spanish detection: '{text[:30]}...' -> {detected}")
        
        # Test English detection
        english_texts = [
            "What are the requirements?",
            "I need information about safety",
            "Quality standards are important"
        ]
        
        for text in english_texts:
            detected = detect_language(text)
            assert detected == "english", f"Expected 'english' for '{text}', got '{detected}'"
            print(f"✅ English detection: '{text[:30]}...' -> {detected}")
        
        print("✅ Language detection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Language detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests for the English KB + Spanish Q&A workflow."""
    print("🧪 Testing English KB + Spanish Q&A Workflow...\n")
    
    tests = [
        test_workflow_optimization,
        test_translation_integration,
        test_language_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The English KB + Spanish Q&A workflow is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
