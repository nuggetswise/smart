#!/usr/bin/env python3
"""
Debug script for scheduling functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.chat_router import ChatRouter

def test_scheduling_debug():
    """Test scheduling with detailed debugging"""
    print("🔍 Debugging Scheduling Functionality...")
    
    try:
        # Initialize chat router
        chat_router = ChatRouter()
        print("✅ Chat router initialized")
        
        # Test message
        test_message = "Set up a meeting with poojapewekar@gmail.com at 1pm today. Send out a meeting invite with link."
        print(f"📝 Test message: {test_message}")
        
        # Check if it's detected as scheduling
        scheduling_keywords = ['schedule', 'book', 'set up', 'meet with', 'appointment', 'call']
        is_scheduling_request = any(keyword in test_message.lower() for keyword in scheduling_keywords)
        print(f"🔍 Scheduling detected: {is_scheduling_request}")
        
        if is_scheduling_request:
            print("🔍 Processing as scheduling request...")
            
            # Extract email
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, test_message)
            print(f"🔍 Found emails: {emails}")
            
            if emails:
                attendee_email = emails[0]
                print(f"🔍 Using attendee email: {attendee_email}")
                
                # Extract time
                time_info = chat_router._extract_time_from_message(test_message)
                print(f"🔍 Extracted time info: {time_info}")
                
                # Generate title
                meeting_title = chat_router._generate_meeting_title(test_message, attendee_email)
                print(f"🔍 Generated title: {meeting_title}")
                
                # Try to create event
                print("🔍 Attempting to create calendar event...")
                try:
                    event_result = chat_router.calendar_tool.add_event(
                        summary=meeting_title,
                        date=time_info['date'],
                        time=time_info['time'],
                        attendees=[attendee_email],
                        location="Google Meet",
                        description=f"Meeting scheduled via SmartDesk AI"
                    )
                    print(f"🔍 Event result: {event_result}")
                    
                    if event_result:
                        response = f"✅ I've scheduled a meeting with {attendee_email} for {time_info['formatted_time']}. The meeting has been added to your calendar and an invitation has been sent."
                        print(f"🔍 Success response: {response}")
                        return True
                    else:
                        print("🔍 Event creation failed")
                        return False
                        
                except Exception as e:
                    print(f"🔍 Error creating event: {e}")
                    return False
            else:
                print("🔍 No email found in message")
                return False
        
        # If not scheduling, test regular conversation
        print("🔍 Processing as regular conversation...")
        response = chat_router.process_user_message(test_message)
        print(f"🔍 Response: {response}")
        
        return "✅" in response or "scheduled" in response.lower()
        
    except Exception as e:
        print(f"❌ Error in debug test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_scheduling_debug()
    print(f"\n📊 Debug Result: {'✅ PASS' if result else '❌ FAIL'}") 