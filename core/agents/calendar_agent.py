"""
SmartDesk AI Calendar Agent
Lightweight, agentic calendar monitoring with AI-powered insights
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging
from core.tools.calendar_tool import CalendarTool
from core.llm_client import LLMClient
import pytz
from core.prompts import build_meeting_insights_prompt

class CalendarAgent:
    """
    Agentic calendar agent that monitors for upcoming meetings
    and provides AI-powered insights and preparation assistance.
    """
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize the calendar agent.
        
        Args:
            check_interval: How often to check for upcoming meetings (seconds)
        """
        self.calendar_tool = CalendarTool()
        self.llm_client = LLMClient()
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        
        # File to store notification history
        self.notification_file = "calendar_notifications.json"
        self.notified_events = self._load_notification_history()
        
        # Notification callback
        self.notification_callback = None
        
        # Agentic capabilities
        self.ai_insights_enabled = True
        self.meeting_prep_enabled = True
        
        # Setup logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
    def _load_notification_history(self) -> Dict[str, Any]:
        """Load notification history from file."""
        try:
            if os.path.exists(self.notification_file):
                with open(self.notification_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading notification history: {e}")
        return {"notified_events": [], "last_check": None}
    
    def _save_notification_history(self):
        """Save notification history to file."""
        try:
            with open(self.notification_file, 'w') as f:
                json.dump(self.notified_events, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving notification history: {e}")
    
    def start_monitoring(self, notification_callback=None):
        """
        Start monitoring for upcoming meetings.
        
        Args:
            notification_callback: Function to call when notification is needed
        """
        if self.running:
            self.logger.warning("Calendar agent is already running")
            return
        
        self.notification_callback = notification_callback
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("Calendar agent started with agentic capabilities")
    
    def stop_monitoring(self):
        """Stop monitoring for upcoming meetings."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("Calendar agent stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self._check_upcoming_meetings()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_upcoming_meetings(self):
        """Check for upcoming meetings and send notifications."""
        try:
            # Get upcoming events
            events = self.calendar_tool.get_upcoming_events_raw()
            if not events:
                return
            
            # Use timezone-aware current time
            current_time = datetime.now(pytz.UTC)
            notifications_sent = []
            
            for event in events:
                event_id = event.get('id')
                if not event_id:
                    continue
                
                # Check if we've already notified about this event
                if event_id in self.notified_events.get("notified_events", []):
                    continue
                
                # Check if event is starting soon (15 minutes)
                start_time = event.get('start', {}).get('dateTime')
                if not start_time:
                    continue
                
                try:
                    event_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    # Ensure event_dt is timezone-aware
                    if event_dt.tzinfo is None:
                        event_dt = pytz.UTC.localize(event_dt)
                    
                    time_until = (event_dt - current_time).total_seconds() / 60  # minutes
                    
                    # Notify if event is starting in 15 minutes or less
                    if 0 <= time_until <= 15:
                        notification = self._create_agentic_meeting_notification(event)
                        notifications_sent.append(notification)
                        
                        # Mark as notified
                        if "notified_events" not in self.notified_events:
                            self.notified_events["notified_events"] = []
                        self.notified_events["notified_events"].append(event_id)
                        
                except Exception as e:
                    self.logger.error(f"Error processing event {event_id}: {e}")
            
            # Send notifications
            if notifications_sent and self.notification_callback:
                for notification in notifications_sent:
                    self.notification_callback(notification)
            
            # Update last check time
            self.notified_events["last_check"] = current_time.isoformat()
            self._save_notification_history()
            
        except Exception as e:
            self.logger.error(f"Error checking upcoming meetings: {e}")
    
    def _create_agentic_meeting_notification(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Create an AI-powered meeting notification with insights."""
        try:
            summary = event.get('summary', 'Unknown Meeting')
            start_time = event.get('start', {}).get('dateTime', '')
            location = event.get('location', 'No location specified')
            description = event.get('description', '')
            attendees = event.get('attendees', [])
            
            # Format attendees
            attendee_list = []
            if attendees:
                for attendee in attendees:
                    email = attendee.get('email', '')
                    name = attendee.get('displayName', email)
                    attendee_list.append(name)
            
            # Format time
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%I:%M %p")
                    formatted_date = dt.strftime("%B %d, %Y")
                except:
                    formatted_time = "TBD"
                    formatted_date = "TBD"
            else:
                formatted_time = "TBD"
                formatted_date = "TBD"
            
            # Generate AI insights if enabled
            ai_insights = ""
            if self.ai_insights_enabled:
                ai_insights = self._generate_meeting_insights(event)
            
            # Create notification message
            message = f"""🔔 **Meeting Reminder**

📅 **{summary}**
🕐 **Time:** {formatted_time} on {formatted_date}
📍 **Location:** {location}"""

            if attendee_list:
                attendee_text = ", ".join(attendee_list[:5])
                if len(attendee_list) > 5:
                    attendee_text += f" and {len(attendee_list) - 5} others"
                message += f"\n👥 **Attendees:** {attendee_text}"

            if description:
                message += f"\n\n📝 **Description:** {description[:200]}..."
                if len(description) > 200:
                    message += " (truncated)"
            
            # Add AI insights
            if ai_insights:
                message += f"\n\n🤖 **AI Insights:**\n{ai_insights}"
            
            message += "\n\n💡 **Need help preparing?** Ask me about the meeting or request a summary of related documents!"
            
            return {
                'type': 'meeting_reminder',
                'content': message,
                'event_id': event.get('id'),
                'event_summary': summary,
                'event_start': start_time,
                'ai_insights': ai_insights,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating meeting notification: {e}")
            return {
                'type': 'meeting_reminder',
                'content': f"🔔 Meeting Reminder: {event.get('summary', 'Unknown Meeting')} - Starting soon!",
                'event_id': event.get('id'),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
    
    def _generate_meeting_insights(self, event: Dict[str, Any]) -> str:
        """Generate AI-powered insights about the meeting."""
        try:
            summary = event.get('summary', '')
            description = event.get('description', '')
            attendees = event.get('attendees', [])
            
            # Build context for AI analysis
            context = f"Meeting: {summary}\n"
            if description:
                context += f"Description: {description}\n"
            if attendees:
                attendee_names = []
                for a in attendees:
                    display_name = a.get('displayName') or a.get('email', '')
                    if display_name:  # Only add non-empty names
                        attendee_names.append(display_name)
                if attendee_names:
                    context += f"Attendees: {', '.join(attendee_names)}\n"
            
            # AI prompt for insights
            prompt = build_meeting_insights_prompt(context)

            # Get AI response
            response = self.llm_client.get_response(prompt, mode="chat")
            
            # Format insights
            insights = response.strip()
            if insights:
                return insights
            else:
                return "Meeting analysis available - ask me for specific insights!"
                
        except Exception as e:
            self.logger.error(f"Error generating meeting insights: {e}")
            return "AI insights temporarily unavailable"
    
    def get_status(self) -> Dict[str, Any]:
        """Get calendar agent status."""
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'last_check': self.notified_events.get('last_check'),
            'notified_count': len(self.notified_events.get('notified_events', [])),
            'thread_alive': self.thread.is_alive() if self.thread else False,
            'ai_insights_enabled': self.ai_insights_enabled,
            'meeting_prep_enabled': self.meeting_prep_enabled
        }
    
    def clear_notification_history(self):
        """Clear notification history."""
        self.notified_events = {"notified_events": [], "last_check": None}
        self._save_notification_history()
        self.logger.info("Notification history cleared")
    
    def test_notification(self) -> Dict[str, Any]:
        """Send a test notification with AI insights."""
        test_event = {
            'id': 'test_event_123',
            'summary': 'Test Meeting with AI Insights',
            'start': {'dateTime': (datetime.now(pytz.UTC) + timedelta(minutes=10)).isoformat()},
            'location': 'Test Conference Room',
            'description': 'This is a test meeting to demonstrate AI-powered calendar agent capabilities',
            'attendees': [
                {'email': 'test@example.com', 'displayName': 'Test User'},
                {'email': 'ai@example.com', 'displayName': 'AI Assistant'}
            ]
        }
        
        notification = self._create_agentic_meeting_notification(test_event)
        return notification
    
    def enable_ai_insights(self, enabled: bool = True):
        """Enable or disable AI insights."""
        self.ai_insights_enabled = enabled
        self.logger.info(f"AI insights {'enabled' if enabled else 'disabled'}")
    
    def enable_meeting_prep(self, enabled: bool = True):
        """Enable or disable meeting preparation features."""
        self.meeting_prep_enabled = enabled
        self.logger.info(f"Meeting preparation {'enabled' if enabled else 'disabled'}") 