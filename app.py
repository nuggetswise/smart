import streamlit as st
from core.chat_router import ChatRouter
from ui.chat_interface import render_chat_interface
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SmartDesk AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main {
        padding: 0;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
    }
    .stButton > button {
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
</style>
""", unsafe_allow_html=True)

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

def handle_user_input():
    """Handle user input and generate agent response."""
    if 'chat_input' in st.session_state and st.session_state.chat_input.strip():
        user_message = st.session_state.chat_input.strip()
        
        # Process message with router
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
                st.session_state.chat_history.append({'role': 'system', 'content': msg})

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Check for proactive agents
    check_proactive_agents()
    
    # Main chat interface
    render_chat_interface()
    
    # Handle user input
    handle_user_input()
    
    # Sidebar for additional controls
    with st.sidebar:
        st.markdown("### SmartDesk AI Controls")
        
        # Model selection
        st.markdown("#### 🤖 LLM Model")
        model_options = {
            "Groq - Gemma2 9B (Primary)": "gemma2-9b-it",
            "Groq - Llama 3.3 70B": "llama-3.3-70b-versatile",
            "Groq - Llama 3.1 8B Instant": "llama-3.1-8b-instant",
            "Gemini 2.0 Flash (Fallback)": "gemini-2.0-flash-exp",
            "OpenAI GPT-3.5": "gpt-3.5-turbo",
            "OpenAI GPT-4o": "gpt-4o"
        }
        
        selected_model = st.selectbox(
            "Choose your AI model:",
            options=list(model_options.keys()),
            index=0,
            help="Select the AI model for responses. Groq models are fastest, Gemini is most cost-effective."
        )
        
        # Store selected model in session state
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = model_options[selected_model]
        else:
            st.session_state.selected_model = model_options[selected_model]
        
        st.markdown(f"**Current Model:** {selected_model}")
        
        if st.button("Clear Chat History"):
            st.session_state.chat_router.clear_memory()
            st.session_state.chat_history = []
            st.session_state.proactive_messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Quick Commands")
        st.markdown("- `/search [query]` - Web search")
        st.markdown("- `/calendar` - Check calendar")
        st.markdown("- `/summarize` - Summarize text")
        
        st.markdown("---")
        st.markdown("### Features")
        st.markdown("✅ OCR from images")
        st.markdown("✅ Calendar integration")
        st.markdown("✅ Web search")
        st.markdown("✅ Persistent memory")
        st.markdown("✅ Proactive agents")

if __name__ == "__main__":
    main() 