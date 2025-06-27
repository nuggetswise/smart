# components/style.py

PRIMARY = '#a78bfa'
SECONDARY = '#f3f4f6'
TEXT_DARK = '#222222'
TEXT_LIGHT = '#6b7280'
CARD_RADIUS = '18px'
BUTTON_RADIUS = '12px'
CARD_SHADOW = '0 2px 16px rgba(80, 80, 120, 0.08)'
BUTTON_HEIGHT = '48px'

STYLE_CSS = f"""
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
"""

def inject_global_styles():
    import streamlit as st
    st.markdown(STYLE_CSS, unsafe_allow_html=True) 