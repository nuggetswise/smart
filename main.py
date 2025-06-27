import streamlit as st
from pathlib import Path
from PIL import Image
import os

# --- Style Guide Variables ---
PRIMARY = '#a78bfa'
SECONDARY = '#f3f4f6'
TEXT_DARK = '#222222'
TEXT_LIGHT = '#6b7280'
CARD_RADIUS = '18px'
BUTTON_RADIUS = '12px'
CARD_SHADOW = '0 2px 16px rgba(80, 80, 120, 0.08)'
BUTTON_HEIGHT = '48px'

st.set_page_config(page_title='SmartDesk AI', page_icon=':bulb:', layout='centered')

# --- Custom CSS ---
st.markdown(f"""
    <style>
    .main {{ background: #fff; }}
    .stButton > button {{
        background: {PRIMARY};
        color: #fff;
        border-radius: {BUTTON_RADIUS};
        height: {BUTTON_HEIGHT};
        font-weight: 600;
        font-size: 1rem;
        margin-right: 16px;
        box-shadow: 0 2px 8px rgba(80, 80, 120, 0.08);
    }}
    .stButton.secondary > button {{
        background: {SECONDARY};
        color: {TEXT_DARK};
        border-radius: {BUTTON_RADIUS};
        font-weight: 600;
        height: {BUTTON_HEIGHT};
        box-shadow: none;
    }}
    .card {{
        background: #fff;
        border-radius: {CARD_RADIUS};
        box-shadow: {CARD_SHADOW};
        padding: 32px;
        margin-bottom: 24px;
    }}
    .icon-circle {{
        background: {PRIMARY};
        border-radius: 50%;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 16px auto;
    }}
    .checkbox-label {{
        font-size: 1rem;
        color: {TEXT_DARK};
        margin-left: 12px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Session State for Onboarding ---
if 'onboarding_step' not in st.session_state:
    st.session_state.onboarding_step = 0
if 'accepted_terms' not in st.session_state:
    st.session_state.accepted_terms = False

# --- Onboarding Wizard ---
def onboarding():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="icon-circle">\U0001F4A1</div>', unsafe_allow_html=True)  # Bulb emoji as logo
    st.markdown('<h2 style="text-align:center; font-weight:700; font-size:2rem;">Welcome to SmartDesk AI!</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#6b7280;">Before you continue, please review and accept our terms of service and privacy policy.</p>', unsafe_allow_html=True)
    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card" style="background:#f3f4f6; box-shadow:none; padding:20px; margin-bottom:16px;">\
        <b>Your data is secure</b><br><span style="color:#6b7280;">We use industry-standard encryption to protect your information.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="background:#f3f4f6; box-shadow:none; padding:20px; margin-bottom:16px;">\
        <b>Personalized experience</b><br><span style="color:#6b7280;">We\'ll use your preferences to customize your productivity assistant.</span></div>', unsafe_allow_html=True)
    
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    col1, _ = st.columns([1,2])
    with col1:
        st.session_state.accepted_terms = st.checkbox(
            'I accept the terms of service and privacy policy',
            value=st.session_state.accepted_terms,
            help='By checking this box, you agree to our Terms of Service and Privacy Policy.'
        )
    st.markdown('<span style="color:#6b7280; font-size:0.95rem;">By checking this box, you agree to our <a href="#" style="color:#a78bfa; text-decoration:underline;">Terms of Service</a> and <a href="#" style="color:#a78bfa; text-decoration:underline;">Privacy Policy</a>.</span>', unsafe_allow_html=True)
    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
    
    colA, colB = st.columns([2,1])
    with colA:
        if st.button('Accept & Continue', use_container_width=True, key='accept', disabled=not st.session_state.accepted_terms):
            st.session_state.onboarding_step = 1
    with colB:
        st.button('Cancel', use_container_width=True, key='cancel', type='secondary')
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Navigation ---
def main_app():
    st.title('SmartDesk AI')
    st.write('Welcome! Choose a productivity tool from the sidebar.')
    st.sidebar.title('SmartDesk AI')
    st.sidebar.markdown('---')
    st.sidebar.button('Image/Note → Action Items')
    st.sidebar.button('Chat Assistant')
    st.sidebar.button('Web Search + Research')
    st.sidebar.button('Calendar Agent')
    st.sidebar.markdown('---')
    st.sidebar.write('Settings, Preferences, and more coming soon!')

# --- App Flow ---
if st.session_state.onboarding_step == 0:
    onboarding()
else:
    main_app() 