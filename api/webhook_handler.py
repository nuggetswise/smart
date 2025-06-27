"""
Webhook Handler for SmartDesk AI Calendar Agent
Phase 1: Basic Integration
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import streamlit as st
from core.tools.calendar_tool import CalendarTool

class WebhookHandler:
    """
    Handles incoming webhooks from Activepieces for calendar notifications.
    Processes meeting reminders and other calendar events.
    """
    
    def __init__(self):
        """Initialize webhook handler."""
        self.logger = logging.getLogger(__name__)
        self.calendar_tool = CalendarTool()
        
    def process_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Process incoming webhook payload from Activepieces.
        
        Args:
            payload: The webhook payload
            headers: Request headers for validation
            
        Returns:
            Response indicating success/failure
        """
        try:
            # Validate webhook
            if not self._validate_webhook(payload, headers):
                return {
                    'success': False,
                    'error': 'Invalid webhook signature or payload',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Extract event type
            event_type = payload.get('event_type', 'unknown')
            
            # Process based on event type
            if event_type == 'meeting_reminder':
                return self._handle_meeting_reminder(payload)
            elif event_type == 'calendar_update':
                return self._handle_calendar_update(payload)
            elif event_type == 'test':
                return self._handle_test_webhook(payload)
            else:
                return {
                    'success': False,
                    'error': f'Unknown event type: {event_type}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error processing webhook: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """
        Validate webhook authenticity and payload structure.
        
        Args:
            payload: The webhook payload
            headers: Request headers
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for required fields
            required_fields = ['event_type', 'timestamp']
            for field in required_fields:
                if field not in payload:
                    self.logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate timestamp (not too old)
            try:
                webhook_time = datetime.fromisoformat(payload['timestamp'].replace('Z', '+00:00'))
                current_time = datetime.now(webhook_time.tzinfo)
                time_diff = abs((current_time - webhook_time).total_seconds())
                
                # Reject webhooks older than 5 minutes
                if time_diff > 300:
                    self.logger.warning(f"Webhook too old: {time_diff} seconds")
                    return False
            except Exception as e:
                self.logger.warning(f"Invalid timestamp format: {e}")
                return False
            
            # TODO: Add signature validation if needed
            # For now, we'll accept all webhooks in development
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating webhook: {e}")
            return False
    
    def _handle_meeting_reminder(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle meeting reminder webhook.
        
        Args:
            payload: Meeting reminder payload
            
        Returns:
            Processing result
        """
        try:
            # Extract meeting information
            event_id = payload.get('event_id')
            event_summary = payload.get('event_summary', 'Unknown Meeting')
            event_start = payload.get('event_start')
            event_location = payload.get('event_location', 'No location specified')
            attendees = payload.get('attendees', [])
            description = payload.get('description', '')
            
            # Create meeting reminder message
            reminder_message = self._create_meeting_reminder_message(
                event_summary, event_start, event_location, attendees, description
            )
            
            # Add to proactive messages in session state
            if 'proactive_messages' not in st.session_state:
                st.session_state.proactive_messages = []
            
            st.session_state.proactive_messages.append({
                'type': 'meeting_reminder',
                'content': reminder_message,
                'event_id': event_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Log the reminder
            self.logger.info(f"Meeting reminder processed: {event_summary}")
            
            return {
                'success': True,
                'message': 'Meeting reminder processed successfully',
                'event_id': event_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling meeting reminder: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_calendar_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle calendar update webhook.
        
        Args:
            payload: Calendar update payload
            
        Returns:
            Processing result
        """
        try:
            # Extract update information
            update_type = payload.get('update_type', 'unknown')
            event_id = payload.get('event_id')
            event_summary = payload.get('event_summary', 'Unknown Event')
            
            # Create update message
            update_message = f"📅 Calendar Update: {update_type.title()} - {event_summary}"
            
            # Add to proactive messages
            if 'proactive_messages' not in st.session_state:
                st.session_state.proactive_messages = []
            
            st.session_state.proactive_messages.append({
                'type': 'calendar_update',
                'content': update_message,
                'event_id': event_id,
                'update_type': update_type,
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"Calendar update processed: {update_type} - {event_summary}")
            
            return {
                'success': True,
                'message': 'Calendar update processed successfully',
                'update_type': update_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling calendar update: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_test_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle test webhook for validation.
        
        Args:
            payload: Test payload
            
        Returns:
            Test response
        """
        return {
            'success': True,
            'message': 'Test webhook received successfully',
            'received_payload': payload,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_meeting_reminder_message(self, summary: str, start_time: str, 
                                       location: str, attendees: list, description: str) -> str:
        """
        Create a formatted meeting reminder message.
        
        Args:
            summary: Meeting summary
            start_time: Meeting start time
            location: Meeting location
            attendees: List of attendees
            description: Meeting description
            
        Returns:
            Formatted reminder message
        """
        try:
            # Parse start time
            if start_time:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%I:%M %p")
                formatted_date = dt.strftime("%B %d, %Y")
            else:
                formatted_time = "TBD"
                formatted_date = "TBD"
            
            # Format attendees
            if attendees and isinstance(attendees, list):
                attendee_list = ", ".join(attendees[:5])  # Limit to first 5
                if len(attendees) > 5:
                    attendee_list += f" and {len(attendees) - 5} others"
            else:
                attendee_list = "No attendees listed"
            
            # Create message
            message = f"""🔔 **Meeting Reminder**

📅 **{summary}**
🕐 **Time:** {formatted_time} on {formatted_date}
📍 **Location:** {location}
👥 **Attendees:** {attendee_list}"""

            if description:
                message += f"\n\n📝 **Description:** {description[:200]}..."
                if len(description) > 200:
                    message += " (truncated)"
            
            message += "\n\n💡 **Need help preparing?** Ask me about the meeting or request a summary of related documents!"
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error creating meeting reminder message: {e}")
            return f"🔔 Meeting Reminder: {summary} - Starting soon!"
    
    def get_pending_messages(self) -> list:
        """
        Get pending proactive messages and clear them.
        
        Returns:
            List of pending messages
        """
        if 'proactive_messages' in st.session_state:
            messages = st.session_state.proactive_messages.copy()
            st.session_state.proactive_messages.clear()
            return messages
        return []
    
    def add_proactive_message(self, message_type: str, content: str, **kwargs):
        """
        Add a proactive message to the queue.
        
        Args:
            message_type: Type of message
            content: Message content
            **kwargs: Additional message data
        """
        if 'proactive_messages' not in st.session_state:
            st.session_state.proactive_messages = []
        
        message = {
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        st.session_state.proactive_messages.append(message)
        self.logger.info(f"Added proactive message: {message_type}") 