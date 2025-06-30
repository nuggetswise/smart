"""
SmartDesk AI - Intelligent Calendar Management and AI Assistant
"""
import streamlit as st
import sys
import os

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.chat_router import ChatRouter
from ui.chat_interface import render_chat_interface
from api.webhook_handler import WebhookHandler
from dotenv import load_dotenv
import json
from datetime import datetime
from core.oauth_handler import show_connect_calendar_button, show_user_info, is_user_authenticated

# Import style function with error handling
try:
    from components.style import apply_custom_style
except ImportError as e:
    st.error(f"Failed to import style module: {e}")
    # Fallback function
    def apply_custom_style():
        st.markdown("""
        <style>
        .main { background: #fff; }
        .stButton > button {
            background: #a78bfa;
            color: #fff;
            border-radius: 12px;
            height: 48px;
            font-weight: 600;
            font-size: 1rem;
            margin-right: 16px;
            box-shadow: 0 2px 8px rgba(80, 80, 120, 0.08);
        }
        </style>
        """, unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Apply custom styling
apply_custom_style()

# Page configuration
st.set_page_config(
    page_title="SmartDesk AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables."""
    if 'chat_router' not in st.session_state:
        st.session_state.chat_router = ChatRouter()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'streaming' not in st.session_state:
        st.session_state.streaming = False
    if 'pending_file' not in st.session_state:
        st.session_state.pending_file = None
    if 'proactive_messages' not in st.session_state:
        st.session_state.proactive_messages = []
    if 'webhook_handler' not in st.session_state:
        st.session_state.webhook_handler = WebhookHandler()
    
    # Calendar agent UI state
    if 'agent_enabled' not in st.session_state:
        st.session_state.agent_enabled = True
    if 'ai_insights_enabled' not in st.session_state:
        st.session_state.ai_insights_enabled = True
    if 'meeting_prep_enabled' not in st.session_state:
        st.session_state.meeting_prep_enabled = True
    if 'notifications_enabled' not in st.session_state:
        st.session_state.notifications_enabled = True
    if 'check_interval' not in st.session_state:
        st.session_state.check_interval = 15

def handle_user_input():
    """Handle user input and generate agent response."""
    if 'chat_input' in st.session_state and st.session_state.chat_input.strip():
        user_message = st.session_state.chat_input.strip()
        selected_tool = st.session_state.get('selected_tool', 'Chat')
        
        # Route based on selected tool
        if selected_tool == 'Search the web':
            response = st.session_state.chat_router._handle_web_search(user_message)
        else:
            response = st.session_state.chat_router.process_user_message(
                user_message, 
                st.session_state.pending_file
            )
        
        # Clear pending file
        st.session_state.pending_file = None
        
        # Update chat history
        st.session_state.chat_history.append({'role': 'user', 'content': user_message})
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        
        # Remove chat_input from session state to prevent infinite rerun loop
        st.session_state.pop('chat_input', None)
        st.rerun()

def check_proactive_agents():
    """Check for proactive agent messages."""
    if st.session_state.chat_router:
        proactive_messages = st.session_state.chat_router.check_proactive_agents()
        for msg in proactive_messages:
            if msg not in st.session_state.proactive_messages:
                st.session_state.proactive_messages.append(msg)
                if isinstance(msg, dict) and 'content' in msg:
                    st.session_state.chat_history.append({'role': 'system', 'content': msg['content']})
                else:
                    st.session_state.chat_history.append({'role': 'system', 'content': str(msg)})
    
    # Check for webhook messages
    if st.session_state.webhook_handler:
        webhook_messages = st.session_state.webhook_handler.get_pending_messages()
        for msg in webhook_messages:
            if isinstance(msg, dict) and 'content' in msg:
                st.session_state.chat_history.append({'role': 'system', 'content': msg['content']})
            else:
                st.session_state.chat_history.append({'role': 'system', 'content': str(msg)})

def render_rich_notification_card(notification):
    """Render a rich notification card with action buttons."""
    if notification.get('type') == 'meeting_reminder':
        with st.container():
            st.markdown(f"""
            <div class="notification-card">
                <h3>🔔 Meeting Reminder</h3>
                <p><strong>{notification.get('event_summary', 'Unknown Meeting')}</strong></p>
                <p>🤖 <em>{notification.get('ai_insights', 'AI insights available')}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 Prepare Meeting", key=f"prepare_{notification.get('event_id', 'unknown')}"):
                    st.success("Meeting preparation started!")
            with col2:
                if st.button("⏰ Remind Later", key=f"remind_{notification.get('event_id', 'unknown')}"):
                    st.info("Reminder set for 5 minutes later")
            with col3:
                if st.button("❌ Dismiss", key=f"dismiss_{notification.get('event_id', 'unknown')}"):
                    st.rerun()

def render_enhanced_sidebar():
    """Render the enhanced sidebar with interactive calendar agent controls."""
    st.markdown("## 🤖 SmartDesk AI")
    
    # Calendar Agent Status Section
    with st.container():
        st.markdown("### 🤖 Calendar Agent Controls")
        
        if st.session_state.chat_router and st.session_state.chat_router.calendar_agent:
            status = st.session_state.chat_router.calendar_agent.get_status()
            
            # Status indicator with enhanced styling
            status_class = "status-unknown"
            status_text = "Unknown"
            status_emoji = "❓"
            
            if status['running'] and status['thread_alive']:
                status_class = "status-healthy"
                status_text = "ACTIVE"
                status_emoji = "🟢"
            elif status['running']:
                status_class = "status-unhealthy"
                status_text = "Starting"
                status_emoji = "🟡"
            else:
                status_class = "status-unhealthy"
                status_text = "Stopped"
                status_emoji = "🔴"
            
            # Status display
            st.markdown(f"""
            <div class="sidebar-section">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div class="status-indicator {status_class}"></div>
                    <span style="font-weight: bold; font-size: 1.1em;">{status_emoji} Agent Status: {status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Agent Settings Section
            st.markdown("#### ⚙️ Agent Settings")
            
            # Main agent toggle
            agent_enabled = st.toggle(
                "🤖 Enable Calendar Agent", 
                value=st.session_state.agent_enabled,
                key="agent_toggle"
            )
            if agent_enabled != st.session_state.agent_enabled:
                st.session_state.agent_enabled = agent_enabled
                if agent_enabled:
                    st.session_state.chat_router.calendar_agent.start_monitoring()
                else:
                    st.session_state.chat_router.calendar_agent.stop_monitoring()
                st.rerun()
            
            # Check interval slider
            check_interval = st.slider(
                "⏱️ Check Interval (minutes)", 
                min_value=1, 
                max_value=60, 
                value=st.session_state.check_interval,
                key="interval_slider"
            )
            if check_interval != st.session_state.check_interval:
                st.session_state.check_interval = check_interval
                st.session_state.chat_router.calendar_agent.check_interval = check_interval * 60
                st.rerun()
            
            # Feature toggles
            ai_insights = st.toggle(
                "🤖 AI Insights", 
                value=st.session_state.ai_insights_enabled,
                key="ai_insights_toggle"
            )
            if ai_insights != st.session_state.ai_insights_enabled:
                st.session_state.ai_insights_enabled = ai_insights
                st.session_state.chat_router.calendar_agent.enable_ai_insights(ai_insights)
                st.rerun()
            
            meeting_prep = st.toggle(
                "📋 Meeting Prep", 
                value=st.session_state.meeting_prep_enabled,
                key="meeting_prep_toggle"
            )
            if meeting_prep != st.session_state.meeting_prep_enabled:
                st.session_state.meeting_prep_enabled = meeting_prep
                st.session_state.chat_router.calendar_agent.enable_meeting_prep(meeting_prep)
                st.rerun()
            
            notifications = st.toggle(
                "🔔 Notifications", 
                value=st.session_state.notifications_enabled,
                key="notifications_toggle"
            )
            if notifications != st.session_state.notifications_enabled:
                st.session_state.notifications_enabled = notifications
                st.rerun()

# --- Consolidated Quick Actions at the bottom ---
def render_quick_action_buttons():
    """Render consolidated quick action buttons in the main chat area."""
    st.markdown("### 🚀 Quick Actions")
    status = st.session_state.chat_router.calendar_agent.get_status() if (st.session_state.chat_router and st.session_state.chat_router.calendar_agent) else {}
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔔 Test Notification", key="quick_test_btn"):
            if st.session_state.chat_router.calendar_agent:
                test_notification = st.session_state.chat_router.calendar_agent.test_notification()
                if 'proactive_messages' not in st.session_state:
                    st.session_state.proactive_messages = []
                st.session_state.proactive_messages.append(test_notification)
                st.success("✅ Test notification sent!")
                st.rerun()
    with col2:
        if st.button("📅 View Calendar", key="quick_calendar_btn"):
            events = st.session_state.chat_router.calendar_tool.get_upcoming_events_raw()
            if not st.session_state.chat_router.calendar_tool.credentials_available:
                st.error(f"Google Calendar API is not active. {st.session_state.chat_router.calendar_tool.error_message}\n\nTo enable calendar features, follow the setup guide in CALENDAR_SETUP.md.")
            elif events:
                st.info(f"📅 Found {len(events)} upcoming events")
                for event in events[:3]:
                    st.write(f"- {event.get('summary', 'Unknown')}")
            else:
                st.info("📅 No upcoming events found")
    with col3:
        if st.button("📊 Agent Stats", key="quick_stats_btn"):
            st.info(f"""
            📊 **Agent Statistics:**
            - Notifications: {status.get('notified_count', 0)}
            - Last Check: {status.get('last_check', '')[:19] if status.get('last_check') else 'Never'}
            - AI Insights: {'Enabled' if status.get('ai_insights_enabled') else 'Disabled'}
            - Meeting Prep: {'Enabled' if status.get('meeting_prep_enabled') else 'Disabled'}
            """)
    with col4:
        if st.button("🔄 Restart Agent", key="quick_restart_btn"):
            if st.session_state.chat_router.calendar_agent:
                st.session_state.chat_router.calendar_agent.stop_monitoring()
                st.session_state.chat_router.calendar_agent.start_monitoring()
                st.success("🔄 Agent restarted successfully!")
                st.rerun()

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Check for proactive agents
    check_proactive_agents()
    
    # Render enhanced sidebar
    with st.sidebar:
        render_enhanced_sidebar()
    
    # Main chat interface
    render_chat_interface()
    
    # Render quick action buttons
    render_quick_action_buttons()
    
    # Handle user input
    handle_user_input()
    
    # Render rich notification cards for proactive messages
    if st.session_state.proactive_messages:
        st.markdown("### 🔔 Recent Notifications")
        for notification in st.session_state.proactive_messages[-3:]:  # Show last 3
            render_rich_notification_card(notification)

if __name__ == "__main__":
    main() 