#!/usr/bin/env python3
"""
Test script for meeting scheduling functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.calendar_tool import CalendarTool
from core.chat_router import ChatRouter
from datetime import datetime, timedelta

def test_calendar_tool_directly():
    """Test the calendar tool's add_event method directly"""
    print("🧪 Testing Calendar Tool Directly...")
    
    try:
        # Initialize calendar tool
        calendar_tool = CalendarTool()
        
        if not calendar_tool.credentials_available:
            print("❌ Calendar credentials not available")
            return False
        
        print("✅ Calendar tool initialized successfully")
        
        # Get tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime('%Y-%m-%d')
        time_str = "14:00"  # 2 PM
        
        print(f"📅 Scheduling test meeting for: {date_str} at {time_str}")
        
        # Try to create a test event
        event_result = calendar_tool.add_event(
            summary="Test Meeting via SmartDesk AI",
            date=date_str,
            time=time_str,
            description="This is a test meeting created by SmartDesk AI",
            location="Google Meet",
            attendees=["09.mandip@gmail.com"],
            duration_minutes=30
        )
        
        if event_result:
            print("✅ Test meeting created successfully!")
            print(f"📧 Event ID: {event_result.get('id', 'Unknown')}")
            print(f"🔗 Event Link: {event_result.get('htmlLink', 'No link available')}")
            return True
        else:
            print("❌ Failed to create test meeting")
            return False
            
    except Exception as e:
        print(f"❌ Error testing calendar tool: {e}")
        return False

def test_chat_router_scheduling():
    """Test the chat router's scheduling logic"""
    print("\n🧪 Testing Chat Router Scheduling Logic...")
    
    try:
        # Initialize chat router
        chat_router = ChatRouter()
        print("✅ Chat router initialized successfully")
        
        # Test message
        test_message = "Schedule a meeting with 09.mandip@gmail.com tomorrow at 3pm EST"
        print(f"📝 Test message: {test_message}")
        
        # Process the message
        response = chat_router.process_user_message(test_message)
        print(f"🤖 Response: {response}")
        
        return "✅" in response
        
    except Exception as e:
        print(f"❌ Error testing chat router: {e}")
        return False

def test_email_invitation():
    """Test if email invitations are being sent"""
    print("\n📧 Testing Email Invitation...")
    
    try:
        calendar_tool = CalendarTool()
        
        if not calendar_tool.credentials_available:
            print("❌ Calendar credentials not available")
            return False
        
        # Create a test event with email invitation
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime('%Y-%m-%d')
        time_str = "15:00"  # 3 PM
        
        print(f"📧 Creating test event with email invitation...")
        
        event_result = calendar_tool.add_event(
            summary="Email Test Meeting",
            date=date_str,
            time=time_str,
            description="Testing email invitation functionality",
            location="Google Meet",
            attendees=["09.mandip@gmail.com"],
            duration_minutes=30
        )
        
        if event_result:
            print("✅ Test event created with email invitation!")
            print("📧 Check your email and 09.mandip@gmail.com for invitations")
            print(f"🔗 Event details: {event_result.get('htmlLink', 'No link')}")
            return True
        else:
            print("❌ Failed to create test event")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email invitation: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SmartDesk AI - Meeting Scheduling Test Suite")
    print("=" * 50)
    
    # Test 1: Direct calendar tool
    test1_result = test_calendar_tool_directly()
    
    # Test 2: Chat router scheduling
    test2_result = test_chat_router_scheduling()
    
    # Test 3: Email invitation
    test3_result = test_email_invitation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Calendar Tool: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Chat Router: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"Email Invitation: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    if test1_result and test2_result and test3_result:
        print("\n🎉 All tests passed! Meeting scheduling is working correctly.")
        print("📧 Check your email and the attendee's email for invitations.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 