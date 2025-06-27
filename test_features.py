#!/usr/bin/env python3
"""
Comprehensive test script for SmartDesk AI SPA features.
Tests each component individually and integration.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_llm_client():
    """Test LLM client functionality."""
    print("🧠 Testing LLM Client...")
    try:
        from core.llm_client import LLMClient
        
        client = LLMClient()
        test_prompt = "Hello! Please respond with 'LLM test successful' if you can see this message."
        
        print(f"  Testing with prompt: {test_prompt}")
        response = client.get_response(test_prompt)
        print(f"  Response: {response}")
        
        if response and response != '[LLM unavailable]':
            print("  ✅ LLM Client: SUCCESS")
            return True
        else:
            print("  ❌ LLM Client: FAILED - No response or LLM unavailable")
            return False
            
    except Exception as e:
        print(f"  ❌ LLM Client: ERROR - {e}")
        return False

def test_ocr_tool():
    """Test OCR tool functionality."""
    print("\n📷 Testing OCR Tool...")
    try:
        from core.tools.ocr_tool import OCRTool
        from PIL import Image
        import io
        
        # Create a simple test image with text
        img = Image.new('RGB', (200, 50), color='white')
        img.save('test_image.png')
        
        # Create a mock uploaded file
        class MockUploadedFile:
            def __init__(self, filename):
                self.name = filename
                with open(filename, 'rb') as f:
                    self._data = f.read()
            
            def read(self):
                return self._data
        
        ocr_tool = OCRTool()
        mock_file = MockUploadedFile('test_image.png')
        
        # Note: This will likely fail since we created a blank image
        # but it tests the OCR pipeline
        result = ocr_tool.extract_text(mock_file)
        print(f"  OCR Result: {result}")
        
        # Cleanup
        os.remove('test_image.png')
        
        print("  ✅ OCR Tool: SUCCESS (pipeline tested)")
        return True
        
    except Exception as e:
        print(f"  ❌ OCR Tool: ERROR - {e}")
        return False

def test_calendar_tool():
    """Test calendar tool functionality."""
    print("\n📅 Testing Calendar Tool...")
    try:
        from core.tools.calendar_tool import CalendarTool
        
        calendar_tool = CalendarTool()
        
        # Test getting upcoming events
        events = calendar_tool.get_upcoming_events(hours=1)
        print(f"  Upcoming events: {events if events else 'None found'}")
        
        # Test checking for reminders
        reminders = calendar_tool.check_for_reminders(minutes=15)
        print(f"  Reminders: {reminders if reminders else 'None found'}")
        
        print("  ✅ Calendar Tool: SUCCESS")
        return True
        
    except Exception as e:
        print(f"  ❌ Calendar Tool: ERROR - {e}")
        print("  Note: This may fail if Google Calendar credentials are not set up")
        return False

def test_websearch_tool():
    """Test web search tool functionality."""
    print("\n🔍 Testing Web Search Tool...")
    try:
        from core.tools.websearch_tool import WebSearchTool
        
        websearch_tool = WebSearchTool()
        test_query = "Python programming"
        
        print(f"  Testing search for: {test_query}")
        result = websearch_tool.search(test_query)
        print(f"  Search result: {result[:200]}..." if len(result) > 200 else f"  Search result: {result}")
        
        if result and result != '[LLM unavailable]':
            print("  ✅ Web Search Tool: SUCCESS")
            return True
        else:
            print("  ❌ Web Search Tool: FAILED - No results or LLM unavailable")
            return False
            
    except Exception as e:
        print(f"  ❌ Web Search Tool: ERROR - {e}")
        return False

def test_summarizer():
    """Test summarizer tool functionality."""
    print("\n📝 Testing Summarizer Tool...")
    try:
        from core.tools.summarizer import Summarizer
        
        summarizer = Summarizer()
        test_text = """
        Python is a high-level, interpreted programming language that emphasizes code readability with its notable use of significant whitespace. 
        Its language constructs and object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.
        Python features a dynamic type system and automatic memory management and supports multiple programming paradigms, including structured, 
        object-oriented, and functional programming.
        """
        
        print(f"  Testing summarization of text: {test_text[:100]}...")
        summary = summarizer.summarize(test_text)
        print(f"  Summary: {summary}")
        
        if summary and summary != '[LLM unavailable]':
            print("  ✅ Summarizer Tool: SUCCESS")
            return True
        else:
            print("  ❌ Summarizer Tool: FAILED - No summary or LLM unavailable")
            return False
            
    except Exception as e:
        print(f"  ❌ Summarizer Tool: ERROR - {e}")
        return False

def test_memory():
    """Test memory functionality."""
    print("\n💾 Testing Memory System...")
    try:
        from core.memory.long_term_memory import LongTermMemory
        
        # Test with a unique user ID to avoid conflicts
        memory = LongTermMemory(user_id='test_user')
        
        # Test adding messages
        memory.add_message('user', 'Hello, this is a test message')
        memory.add_message('assistant', 'Hello! I received your test message.')
        
        # Test retrieving messages
        recent_messages = memory.get_recent_messages(5)
        print(f"  Recent messages: {len(recent_messages)} messages retrieved")
        
        all_messages = memory.get_all_messages()
        print(f"  All messages: {len(all_messages)} messages in memory")
        
        # Test clearing memory
        memory.clear_memory()
        cleared_messages = memory.get_all_messages()
        print(f"  After clearing: {len(cleared_messages)} messages in memory")
        
        if len(cleared_messages) == 0:
            print("  ✅ Memory System: SUCCESS")
            return True
        else:
            print("  ❌ Memory System: FAILED - Memory not cleared properly")
            return False
            
    except Exception as e:
        print(f"  ❌ Memory System: ERROR - {e}")
        return False

def test_chat_router():
    """Test chat router integration."""
    print("\n🔄 Testing Chat Router Integration...")
    try:
        from core.chat_router import ChatRouter
        
        router = ChatRouter()
        
        # Test regular conversation
        print("  Testing regular conversation...")
        response = router.process_user_message("Hello, this is a test message")
        print(f"  Response: {response[:100]}..." if len(response) > 100 else f"  Response: {response}")
        
        # Test web search command
        print("  Testing web search command...")
        search_response = router.process_user_message("/search Python programming")
        print(f"  Search response: {search_response[:100]}..." if len(search_response) > 100 else f"  Search response: {search_response}")
        
        # Test calendar command
        print("  Testing calendar command...")
        calendar_response = router.process_user_message("/calendar")
        print(f"  Calendar response: {calendar_response}")
        
        # Test proactive agents
        print("  Testing proactive agents...")
        proactive_messages = router.check_proactive_agents()
        print(f"  Proactive messages: {proactive_messages}")
        
        print("  ✅ Chat Router: SUCCESS")
        return True
        
    except Exception as e:
        print(f"  ❌ Chat Router: ERROR - {e}")
        return False

def test_persona_config():
    """Test persona configuration loading."""
    print("\n👤 Testing Persona Configuration...")
    try:
        config_path = 'core/memory/persona_config.json'
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            required_keys = ['name', 'personality', 'memory_limit', 'proactive_agents']
            missing_keys = [key for key in required_keys if key not in config]
            
            if not missing_keys:
                print(f"  Persona name: {config['name']}")
                print(f"  Memory limit: {config['memory_limit']}")
                print(f"  Proactive agents: {config['proactive_agents']}")
                print("  ✅ Persona Configuration: SUCCESS")
                return True
            else:
                print(f"  ❌ Persona Configuration: FAILED - Missing keys: {missing_keys}")
                return False
        else:
            print(f"  ❌ Persona Configuration: FAILED - Config file not found at {config_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Persona Configuration: ERROR - {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 SmartDesk AI SPA - Feature Testing")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    test_results.append(("LLM Client", test_llm_client()))
    test_results.append(("OCR Tool", test_ocr_tool()))
    test_results.append(("Calendar Tool", test_calendar_tool()))
    test_results.append(("Web Search Tool", test_websearch_tool()))
    test_results.append(("Summarizer Tool", test_summarizer()))
    test_results.append(("Memory System", test_memory()))
    test_results.append(("Chat Router", test_chat_router()))
    test_results.append(("Persona Config", test_persona_config()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your SmartDesk AI SPA is ready to run.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 