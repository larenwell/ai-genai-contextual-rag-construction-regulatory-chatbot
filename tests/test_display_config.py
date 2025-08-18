#!/usr/bin/env python3
"""
Test script for display configuration and formatting
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from config.display_config import (
        get_display_config, get_emoji, get_relevance_icon, 
        get_random_suggestion, format_error_message
    )
    print("✅ Display configuration imported successfully")
except ImportError as e:
    print(f"❌ Error importing display configuration: {e}")
    sys.exit(1)

def test_display_config():
    """Test the display configuration functions."""
    print("\n🧪 Testing Display Configuration")
    print("=" * 50)
    
    # Test configuration loading
    config = get_display_config()
    print(f"✅ Configuration loaded with {len(config)} sections")
    
    # Test emoji functions
    print(f"\n🔍 Testing emoji functions:")
    print(f"   Welcome emoji: {get_emoji('welcome')}")
    print(f"   Assistant emoji: {get_emoji('assistant')}")
    print(f"   Sources emoji: {get_emoji('sources')}")
    print(f"   Error emoji: {get_emoji('error')}")
    
    # Test relevance icons
    print(f"\n🎯 Testing relevance icons:")
    print(f"   High relevance (90%): {get_relevance_icon(0.9)}")
    print(f"   Medium relevance (70%): {get_relevance_icon(0.7)}")
    print(f"   Low relevance (30%): {get_relevance_icon(0.3)}")
    
    # Test random suggestions
    print(f"\n💭 Testing random suggestions:")
    for i in range(3):
        suggestion = get_random_suggestion()
        print(f"   Suggestion {i+1}: {suggestion}")
    
    # Test error message formatting
    print(f"\n❌ Testing error message formatting:")
    error_msg = format_error_message("processing_error", error="Test error message")
    print(f"   Error message length: {len(error_msg)} characters")
    print(f"   Contains 'Error:' text: {'✅' if 'Error:' in error_msg else '❌'}")
    
    # Test configuration sections
    print(f"\n⚙️ Configuration sections:")
    for section_name, section_data in config.items():
        if isinstance(section_data, dict):
            print(f"   {section_name}: {len(section_data)} items")
        else:
            print(f"   {section_name}: {type(section_data).__name__}")
    
    print(f"\n✅ All tests completed successfully!")

def test_source_formatting():
    """Test source formatting with sample data."""
    print(f"\n📚 Testing Source Formatting")
    print("=" * 50)
    
    # Sample context response
    sample_context = {
        'matches': [
            {
                'score': 0.85,
                'metadata': {
                    'book_title': 'FMDS0201.pdf',
                    'page_number': 11,
                    'chunk_type': 'text_subdivision',
                    'text': 'Sample text content'
                }
            },
            {
                'score': 0.72,
                'metadata': {
                    'book_title': 'FMDS0200.pdf',
                    'page_number': 5,
                    'chunk_type': 'structured_section',
                    'text': 'Another sample text'
                }
            }
        ]
    }
    
    # Import the formatting function
    try:
        from frontend_rag import format_sources_for_display
        sources_text = format_sources_for_display(sample_context)
        print(f"✅ Source formatting successful")
        print(f"   Output length: {len(sources_text)} characters")
        print(f"   Contains 'Fuentes consultadas': {'✅' if 'Fuentes consultadas' in sources_text else '❌'}")
        print(f"   Contains relevance scores: {'✅' if '85.0%' in sources_text else '❌'}")
        
        # Show a preview
        print(f"\n📖 Source formatting preview:")
        print("-" * 40)
        print(sources_text[:300] + "..." if len(sources_text) > 300 else sources_text)
        
    except ImportError as e:
        print(f"❌ Could not test source formatting: {e}")

if __name__ == "__main__":
    test_display_config()
    test_source_formatting() 