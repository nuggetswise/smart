"""
Calendar agent using google-calendar-simple-api (gcsa).
"""
from gcsa.google_calendar import GoogleCalendar
from datetime import datetime, timedelta, date
import streamlit as st
import os
import json
import pytz

class CalendarTool:
    """
    Calendar agent for polling and monitoring Google Calendar events.
    """
    def __init__(self):
        self.credentials_available = False
        self.error_message = "Unknown error"
        self.calendar = None
        
        # Check for credentials in multiple locations
        credential_paths = [
            'credentials.json',
            'token.json',
            '.credentials/credentials.json',
            '.credentials/token.json',
            os.path.expanduser('~/.credentials/credentials.json'),
            os.path.expanduser('~/.credentials/token.json')
        ]
        
        credentials_found = False
        for path in credential_paths:
            if os.path.exists(path):
                credentials_found = True
                print(f"Found credentials at: {path}")
                break
        
        if not credentials_found:
            self.error_message = "No credential files found. Please set up Google Calendar API credentials."
            return
        
        try:
            # Try to initialize Google Calendar
            self.calendar = GoogleCalendar()
            self.credentials_available = True
            print("Calendar tool initialized successfully")
        except Exception as e:
            self.credentials_available = False
            self.error_message = str(e)
            print(f"Calendar initialization failed: {e}")
    
    def _get_timezone_aware_now(self):
        """Get timezone-aware current time."""
        try:
            # Try to get local timezone
            local_tz = pytz.timezone('America/Toronto')  # Default to Toronto timezone
            return datetime.now(local_tz)
        except:
            # Fallback to UTC
            return datetime.now(pytz.UTC)
    
    def _make_timezone_aware(self, dt):
        """Make a datetime object timezone-aware."""
        if dt is None:
            return None
        
        try:
            # If it's already timezone-aware, return as is
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                return dt
            
            # If it's a date object, convert to datetime first
            if isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, datetime.min.time())
            
            # If it's a naive datetime, assume local timezone
            if isinstance(dt, datetime) and dt.tzinfo is None:
                # Use local timezone
                local_tz = pytz.timezone('America/Toronto')  # Default to Toronto timezone
                dt = local_tz.localize(dt)
            
            return dt
        except Exception as e:
            # If we can't make it timezone-aware, assume UTC
            print(f"Error making datetime timezone-aware: {e}")
            if isinstance(dt, datetime):
                return pytz.UTC.localize(dt)
            else:
                return dt
    
    def _compare_datetime(self, dt1, dt2):
        """Compare two datetime objects, handling both date and datetime types."""
        try:
            # Convert both to datetime if they're dates
            if isinstance(dt1, date) and not isinstance(dt1, datetime):
                dt1 = datetime.combine(dt1, datetime.min.time())
            if isinstance(dt2, date) and not isinstance(dt2, datetime):
                dt2 = datetime.combine(dt2, datetime.min.time())
            
            # Make both timezone-aware
            dt1 = self._make_timezone_aware(dt1)
            dt2 = self._make_timezone_aware(dt2)
            
            return dt1, dt2
        except Exception as e:
            # If we can't handle the comparison, raise a more specific error
            raise ValueError(f"Unable to compare datetime objects: {e}")
    
    def _safe_datetime_comparison(self, event_start, compare_time):
        """Safely compare event start time with a comparison time, handling date vs datetime."""
        try:
            # If event_start is a date, convert to datetime
            if isinstance(event_start, date) and not isinstance(event_start, datetime):
                event_start = datetime.combine(event_start, datetime.min.time())
            
            # Make both timezone-aware
            event_start = self._make_timezone_aware(event_start)
            compare_time = self._make_timezone_aware(compare_time)
            
            return event_start, compare_time
        except Exception as e:
            # If we can't handle the comparison, return None to indicate skip
            print(f"Error in datetime comparison: {e}")
            return None, None
    
    def _is_all_day_event(self, event):
        """Check if an event is an all-day event."""
        try:
            # Check if start or end is a date (not datetime)
            start_is_date = isinstance(event.start, date) and not isinstance(event.start, datetime)
            end_is_date = isinstance(event.end, date) and not isinstance(event.end, datetime)
            
            # Check if the event has date-only fields (no time component)
            if hasattr(event, 'start'):
                if hasattr(event.start, 'date') and not hasattr(event.start, 'hour'):
                    return True
                # Also check if it's a date object (but NOT a datetime object)
                if isinstance(event.start, date) and not isinstance(event.start, datetime):
                    return True
                # Check if it's a datetime but represents an all-day event
                if isinstance(event.start, datetime):
                    # If start time is midnight and end time is midnight next day, it's all-day
                    if (event.start.hour == 0 and event.start.minute == 0 and 
                        hasattr(event, 'end') and isinstance(event.end, datetime) and
                        event.end.hour == 0 and event.end.minute == 0):
                        return True
            
            # Check for birthday events by summary (more specific)
            if hasattr(event, 'summary') and event.summary:
                summary_lower = event.summary.lower()
                # Only mark as all-day if it's clearly a birthday event
                if any(keyword in summary_lower for keyword in ['birthday', 'birth day', 'bday']) and 'birthday' in summary_lower:
                    return True
            
            return start_is_date or end_is_date
        except Exception as e:
            # If we can't determine, assume it's not all-day to be safe
            print(f"Error checking if event is all-day: {e}")
            return False
    
    def _get_event_uid(self, event):
        """Safely get event UID with fallback."""
        try:
            if hasattr(event, 'uid') and event.uid:
                return event.uid
            else:
                # Create a fallback UID based on summary and start time
                start_str = str(event.start) if hasattr(event, 'start') else 'unknown'
                summary = getattr(event, 'summary', 'unknown')
                return f"fallback_{hash(f'{summary}_{start_str}')}"
        except:
            return f"fallback_{hash(str(event))}"
    
    def get_upcoming_events(self, hours=24):
        """
        Get upcoming events in the next `hours` hours.
        """
        if not self.credentials_available:
            return f"Calendar credentials not configured. Please set up Google Calendar API credentials.\nError: {self.error_message}"
        
        try:
            now = self._get_timezone_aware_now()
            end_time = now + timedelta(hours=hours)
            
            events = []
            for event in self.calendar:
                try:
                    # Skip all-day events for upcoming events (they're usually not time-sensitive)
                    if self._is_all_day_event(event):
                        continue
                    
                    # Use the safe comparison method to handle date/datetime properly
                    event_start, now_comp = self._safe_datetime_comparison(event.start, now)
                    if event_start is None or now_comp is None:
                        continue  # Skip events with comparison issues
                    
                    _, end_time_comp = self._safe_datetime_comparison(event.start, end_time)
                    if end_time_comp is None:
                        continue
                    
                    if event_start >= now_comp and event_start <= end_time_comp:
                        events.append(event)
                except Exception as e:
                    print(f"Error processing event {getattr(event, 'summary', 'Unknown')}: {e}")
                    # Skip this event and continue
                    continue
            
            if not events:
                return f"No upcoming events found in the next {hours} hours."
            
            lines = []
            for event in events:
                try:
                    start_time = event.start.strftime('%Y-%m-%d %H:%M')
                    lines.append(f'- {event.summary} at {start_time}')
                except Exception as e:
                    print(f"Error formatting event {getattr(event, 'summary', 'Unknown')}: {e}")
                    continue
            return '\n'.join(lines)
        except Exception as e:
            return f"Error accessing calendar: {str(e)}"
    
    def get_upcoming_events_raw(self, hours=24):
        """
        Get upcoming events as raw data for the calendar agent.
        Returns list of event dictionaries.
        """
        if not self.credentials_available:
            return []
        
        try:
            now = self._get_timezone_aware_now()
            end_time = now + timedelta(hours=hours)
            
            events = []
            for event in self.calendar:
                try:
                    event_summary = getattr(event, 'summary', 'Unknown Event')
                    
                    # Skip all-day events (birthdays, etc.) - they're not time-sensitive meetings
                    if self._is_all_day_event(event):
                        continue
                    
                    # Check if event has a valid start time
                    if not hasattr(event, 'start') or event.start is None:
                        continue
                    
                    # Use the safe comparison method to handle date/datetime properly
                    event_start, now_comp = self._safe_datetime_comparison(event.start, now)
                    if event_start is None or now_comp is None:
                        continue  # Skip events with comparison issues
                    
                    _, end_time_comp = self._safe_datetime_comparison(event.start, end_time)
                    if end_time_comp is None:
                        continue
                    
                    # Check if event is in the future and within our time window
                    if event_start >= now_comp and event_start <= end_time_comp:
                        # Convert event to dictionary format
                        event_dict = {
                            'id': self._get_event_uid(event),
                            'summary': event_summary,
                            'description': getattr(event, 'description', ''),
                            'location': getattr(event, 'location', ''),
                            'start': {
                                'dateTime': event_start.isoformat(),
                                'timeZone': str(event_start.tzinfo)
                            },
                            'end': {
                                'dateTime': self._make_timezone_aware(event.end).isoformat(),
                                'timeZone': str(self._make_timezone_aware(event.end).tzinfo)
                            },
                            'attendees': []
                        }
                        
                        # Add attendees if available
                        if hasattr(event, 'attendees') and event.attendees:
                            for attendee in event.attendees:
                                event_dict['attendees'].append({
                                    'email': attendee.email,
                                    'displayName': getattr(attendee, 'display_name', attendee.email),
                                    'responseStatus': getattr(attendee, 'response_status', 'needsAction')
                                })
                        
                        events.append(event_dict)
                        
                except Exception as e:
                    # Log error but don't print to console to avoid spam
                    # print(f"Error processing event {getattr(event, 'summary', 'Unknown')}: {e}")
                    continue
            
            return events
            
        except Exception as e:
            print(f"Error accessing calendar: {e}")
            return []
    
    def check_for_reminders(self, minutes=15):
        """
        Check for events in the next `minutes` minutes and return proactive reminders.
        Uses st.session_state to avoid duplicate notifications.
        """
        if not self.credentials_available:
            return ""
        
        try:
            now = self._get_timezone_aware_now()
            soon = now + timedelta(minutes=minutes)
            reminders = []
            
            # Initialize notified events set if not exists
            if 'notified_events' not in st.session_state:
                st.session_state.notified_events = set()
            
            # Check for upcoming events
            for event in self.calendar:
                try:
                    # Skip all-day events for proactive reminders (they're usually not urgent)
                    if self._is_all_day_event(event):
                        continue
                    
                    # Use the safe comparison method to handle date/datetime properly
                    event_start, now_comp = self._safe_datetime_comparison(event.start, now)
                    if event_start is None or now_comp is None:
                        continue  # Skip events with comparison issues
                    
                    _, soon_comp = self._safe_datetime_comparison(event.start, soon)
                    if soon_comp is None:
                        continue
                    
                    if event_start >= now_comp and event_start <= soon_comp:
                        # Create unique identifier for this event
                        event_uid = self._get_event_uid(event)
                        event_id = f"{event_uid}_{event_start.strftime('%Y%m%d_%H%M')}"
                        
                        if event_id not in st.session_state.notified_events:
                            mins = int((event_start - now_comp).total_seconds() // 60)
                            
                            # Format the reminder message
                            if mins == 0:
                                time_text = "now"
                            elif mins == 1:
                                time_text = "1 minute"
                            else:
                                time_text = f"{mins} minutes"
                            
                            # Add location if available
                            location_info = ""
                            if hasattr(event, 'location') and event.location:
                                location_info = f" at {event.location}"
                            
                            reminder_msg = f"🔔 **Meeting Reminder**: You have '{event.summary}' starting in {time_text}{location_info}"
                            reminders.append(reminder_msg)
                            
                            # Mark as notified
                            st.session_state.notified_events.add(event_id)
                            
                except Exception as e:
                    print(f"Error processing event for reminder: {e}")
                    continue
            
            return '\n'.join(reminders) if reminders else ""
            
        except Exception as e:
            print(f"Error checking reminders: {e}")
            return ""
    
    def get_calendar_status(self):
        """
        Get detailed status information about the calendar connection.
        """
        status = {
            "credentials_available": self.credentials_available,
            "error_message": self.error_message,
            "calendar_initialized": self.calendar is not None
        }
        
        if self.credentials_available:
            try:
                # Try to get a sample of events to verify connection
                now = self._get_timezone_aware_now()
                end_time = now + timedelta(hours=1)
                
                sample_events = []
                for event in self.calendar:
                    try:
                        # Skip all-day events for status check
                        if self._is_all_day_event(event):
                            continue
                        
                        event_start = self._make_timezone_aware(event.start)
                        if event_start >= now and event_start <= end_time:
                            sample_events.append(event)
                    except Exception as e:
                        # Skip problematic events
                        continue
                
                status["connection_test"] = "success"
                status["sample_events_count"] = len(sample_events)
            except Exception as e:
                status["connection_test"] = "failed"
                status["connection_error"] = str(e)
        
        return status

def poll():
    """
    Poll for upcoming events in the next 2 hours.
    """
    try:
        calendar = GoogleCalendar()
        now = datetime.now(pytz.UTC)  # Use timezone-aware datetime
        events = []
        for event in calendar:
            try:
                # Skip all-day events
                if isinstance(event.start, date) and not isinstance(event.start, datetime):
                    continue
                
                event_start = event.start
                if isinstance(event_start, date) and not isinstance(event_start, datetime):
                    event_start = datetime.combine(event_start, datetime.min.time())
                
                if hasattr(event_start, 'tzinfo') and event_start.tzinfo is None:
                    event_start = pytz.UTC.localize(event_start)
                
                if event_start >= now and event_start <= now + timedelta(hours=2):
                    events.append(event)
            except Exception as e:
                print(f"Error processing event in poll: {e}")
                continue
        return events
    except Exception as e:
        print(f"Error in poll function: {e}")
        return []

def monitor_calendar_events():
    """
    Check for events in the next 15 minutes and return reminders. Uses st.session_state to avoid duplicates.
    """
    try:
        calendar = GoogleCalendar()
        now = datetime.now(pytz.UTC)  # Use timezone-aware datetime
        soon = now + timedelta(minutes=15)
        reminders = []
        if 'notified_events' not in st.session_state:
            st.session_state.notified_events = set()
        for event in calendar:
            try:
                # Skip all-day events
                if isinstance(event.start, date) and not isinstance(event.start, datetime):
                    continue
                
                event_start = event.start
                if isinstance(event_start, date) and not isinstance(event_start, datetime):
                    event_start = datetime.combine(event_start, datetime.min.time())
                
                if hasattr(event_start, 'tzinfo') and event_start.tzinfo is None:
                    event_start = pytz.UTC.localize(event_start)
                
                if event_start >= now and event_start <= soon:
                    event_uid = getattr(event, 'uid', f"fallback_{hash(str(event))}")
                    if event_uid not in st.session_state.notified_events:
                        minutes = int((event_start - now).total_seconds() // 60)
                        reminders.append(f'🔔 *Reminder: You have a meeting in {minutes} mins – "{event.summary}"*')
                        st.session_state.notified_events.add(event_uid)
            except Exception as e:
                print(f"Error processing event in monitor_calendar_events: {e}")
                continue
        return reminders
    except Exception as e:
        print(f"Error in monitor_calendar_events function: {e}")
        return [] 