import streamlit as st
from typing import Optional

def handle_upload() -> Optional[object]:
    """
    Handles file/image uploads from the chat interface. Supports PNG, JPG, JPEG, PDF. Returns uploaded file object or None.
    """
    try:
        uploaded_file = st.file_uploader('Upload an image or PDF', type=['png', 'jpg', 'jpeg', 'pdf'], key='file_upload')
        if uploaded_file:
            # Show a subtle indicator that file is ready
            st.markdown(f'<div style="background:#e8f5e8; padding:8px 12px; border-radius:8px; margin-bottom:8px; border-left:3px solid #4caf50; font-size:0.9rem;">📎 {uploaded_file.name} ready to process</div>', unsafe_allow_html=True)
            return uploaded_file
        return None
    except Exception as e:
        st.error(f'Upload failed: {e}')
        return None 