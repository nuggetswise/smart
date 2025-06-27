import streamlit as st
from ui.upload_handler import handle_upload
import streamlit.components.v1 as components

# Helper to render a single message (user or assistant)
def render_message(message, is_user=False, is_system=False):
    if is_system:
        # System messages (proactive agents)
        st.markdown(f'''
        <div style="background:#e3f2fd; padding:12px 16px; border-radius:16px; margin-bottom:8px; border-left:4px solid #2196f3;">
            <span style="font-size:1.2em;">🔔</span>  <span style="white-space:pre-wrap;">{message}</span>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    avatar = '🧑' if is_user else '🤖'
    align = 'flex-end' if is_user else 'flex-start'
    bubble_color = '#DCF8C6' if is_user else '#F1F0F0'
    st.markdown(f'''
    <div style="display:flex; justify-content:{align}; margin-bottom:8px;">
        <div style="background:{bubble_color}; padding:12px 16px; border-radius:16px; max-width:70%;">
            <span style="font-size:1.2em;">{avatar}</span>  <span style="white-space:pre-wrap;">{message}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_chat_interface():
    """
    Renders the persistent chat thread UI with markdown, streaming, file upload, and system messages.
    """
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center; font-weight:700; font-size:2rem;">SmartDesk AI Assistant</h2>', unsafe_allow_html=True)
    
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'streaming' not in st.session_state:
        st.session_state.streaming = False
    if 'pending_file' not in st.session_state:
        st.session_state.pending_file = None
    if 'selected_tool' not in st.session_state:
        st.session_state.selected_tool = 'Chat'

    # Tool selector
    tool = st.selectbox(
        'Choose a tool:',
        ['Chat', 'Search the web'],
        index=0,
        key='selected_tool',
        help='Select how you want to process your message.'
    )

    # File/image upload
    uploaded_file = handle_upload()
    if uploaded_file and uploaded_file != st.session_state.get('pending_file'):
        st.session_state.pending_file = uploaded_file
        # Don't rerun - just store the file and continue

    # Show pending file indicator
    if st.session_state.pending_file:
        st.markdown(f'<div style="background:#fff3cd; padding:8px 12px; border-radius:8px; margin-bottom:8px; border-left:3px solid #ffc107; font-size:0.9rem;">📎 File "{st.session_state.pending_file.name}" will be included with your next message</div>', unsafe_allow_html=True)

    # Render chat history from session state
    for msg in st.session_state.chat_history:
        if msg['role'] == 'system':
            render_message(msg['content'], is_system=True)
        else:
            render_message(msg['content'], is_user=(msg['role']=='user'))

    # User input
    # Add a hidden form to allow Enter-to-send
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var textarea = document.querySelector('textarea[data-testid=\"stTextArea\"]');
        if (textarea) {
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    document.querySelector('form').requestSubmit();
                }
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)
    with st.form('chat_input_form', clear_on_submit=True):
        user_input = st.text_area('Type your message...', key='chat_input', height=68)
        submitted = st.form_submit_button('Send')
    
    if submitted and user_input.strip():
        # The actual processing is handled in app.py's handle_user_input()
        pass

    # Streaming/agent response placeholder
    if st.session_state.streaming:
        render_message('Thinking... (streaming)', is_user=False)

    st.markdown('</div>', unsafe_allow_html=True) 