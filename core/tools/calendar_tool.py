"""
Calendar agent using google-calendar-simple-api (gcsa).
"""
from gcsa.google_calendar import GoogleCalendar
from datetime import datetime, timedelta
import streamlit as st

class CalendarTool:
    """
    Calendar agent for polling and monitoring Google Calendar events.
    """
    def __init__(self):
        try:
            self.calendar = GoogleCalendar()
            self.credentials_available = True
        except Exception as e:
            self.credentials_available = False
            self.error_message = str(e)
    
    def get_upcoming_events(self, hours=2):
        """
        Get upcoming events in the next `hours` hours.
        """
        if not self.credentials_available:
            return "Calendar credentials not configured. Please set up Google Calendar API credentials."
        
        try:
            now = datetime.now()
            events = [event for event in self.calendar if event.start >= now and event.start <= now + timedelta(hours=hours)]
            if not events:
                return ""
            lines = []
            for event in events:
                start_time = event.start.strftime('%Y-%m-%d %H:%M')
                lines.append(f'- {event.summary} at {start_time}')
            return '\n'.join(lines)
        except Exception as e:
            return f"Error accessing calendar: {str(e)}"
    
    def check_for_reminders(self, minutes=15):
        """
        Check for events in the next `minutes` minutes and return reminders. Uses st.session_state to avoid duplicates.
        """
        if not self.credentials_available:
            return ""
        
        try:
            now = datetime.now()
            soon = now + timedelta(minutes=minutes)
            reminders = []
            if 'notified_events' not in st.session_state:
                st.session_state.notified_events = set()
            for event in self.calendar:
                if event.start >= now and event.start <= soon:
                    if event.uid not in st.session_state.notified_events:
                        mins = int((event.start - now).total_seconds() // 60)
                        reminders.append(f'🔔 *Reminder: You have a meeting in {mins} mins – "{event.summary}"*')
                        st.session_state.notified_events.add(event.uid)
            return '\n'.join(reminders) if reminders else ""
        except Exception as e:
            return f"Error checking reminders: {str(e)}"

def poll():
    """
    Poll for upcoming events in the next 2 hours.
    """
    calendar = GoogleCalendar()
    now = datetime.now()
    events = [event for event in calendar if event.start >= now and event.start <= now + timedelta(hours=2)]
    return events

def monitor_calendar_events():
    """
    Check for events in the next 15 minutes and return reminders. Uses st.session_state to avoid duplicates.
    """
    calendar = GoogleCalendar()
    now = datetime.now()
    soon = now + timedelta(minutes=15)
    reminders = []
    if 'notified_events' not in st.session_state:
        st.session_state.notified_events = set()
    for event in calendar:
        if event.start >= now and event.start <= soon:
            if event.uid not in st.session_state.notified_events:
                minutes = int((event.start - now).total_seconds() // 60)
                reminders.append(f'🔔 *Reminder: You have a meeting in {minutes} mins – "{event.summary}"*')
                st.session_state.notified_events.add(event.uid)
    return reminders 