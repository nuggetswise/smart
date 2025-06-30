
# oauth_handler.py
import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import os

class OAuthHandler:
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
    def get_auth_url(self):
        """Generate OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        flow.redirect_uri = self.redirect_uri
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def exchange_code_for_tokens(self, code):
        """Exchange authorization code for access/refresh tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        flow.redirect_uri = self.redirect_uri
        flow.fetch_token(code=code)
        return flow.credentials

def oauth_callback():
    """Handle OAuth callback in Streamlit"""
    if 'code' in st.experimental_get_query_params():
        code = st.experimental_get_query_params()['code'][0]
        oauth_handler = OAuthHandler()
        credentials = oauth_handler.exchange_code_for_tokens(code)
        
        # Store credentials in session state
        st.session_state.user_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        st.success("✅ Calendar connected successfully!")
        st.rerun()

def show_connect_calendar_button():
    """Show connect calendar button if user not authenticated"""
    if 'user_credentials' not in st.session_state:
        oauth_handler = OAuthHandler()
        auth_url = oauth_handler.get_auth_url()
        
        st.markdown("### 🔗 Connect Your Calendar")
        st.markdown("To use calendar features, please connect your Google Calendar:")
        
        if st.button("🔗 Connect Google Calendar"):
            st.markdown(f"[Click here to authorize]({auth_url})")
