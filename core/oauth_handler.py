"""
OAuth2 Handler for Google Calendar Integration
"""
import streamlit as st
import requests
import json
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import base64
import hashlib

class OAuthHandler:
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501/oauth/callback')
        
        # OAuth scopes for Google Calendar
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/userinfo.email'
        ]
    
    def get_auth_url(self, state=None):
        """Generate OAuth authorization URL"""
        if not self.client_id or not self.client_secret:
            st.error("❌ OAuth credentials not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
            return None
        
        # Generate state parameter for security
        if not state:
            state = self._generate_state()
        
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
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        # Add state parameter for security
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )
        
        return auth_url, state
    
    def exchange_code_for_tokens(self, code, state=None):
        """Exchange authorization code for access/refresh tokens"""
        try:
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
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            flow.fetch_token(code=code)
            
            # Get user info
            user_info = self._get_user_info(flow.credentials.token)
            
            return {
                'token': flow.credentials.token,
                'refresh_token': flow.credentials.refresh_token,
                'token_uri': flow.credentials.token_uri,
                'client_id': flow.credentials.client_id,
                'client_secret': flow.credentials.client_secret,
                'scopes': flow.credentials.scopes,
                'expiry': flow.credentials.expiry.isoformat() if flow.credentials.expiry else None,
                'user_email': user_info.get('email'),
                'user_name': user_info.get('name'),
                'connected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.error(f"❌ Failed to exchange code for tokens: {e}")
            return None
    
    def refresh_tokens(self, refresh_token):
        """Refresh access token using refresh token"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )
            
            # Refresh the token
            credentials.refresh(Request())
            
            return {
                'token': credentials.token,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
        except Exception as e:
            st.error(f"❌ Failed to refresh tokens: {e}")
            return None
    
    def _get_user_info(self, access_token):
        """Get user information from Google"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            if response.ok:
                return response.json()
            else:
                return {}
        except Exception:
            return {}
    
    def _generate_state(self):
        """Generate a secure state parameter"""
        import secrets
        return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    
    def is_token_expired(self, credentials_data):
        """Check if the access token is expired"""
        if not credentials_data.get('expiry'):
            return True
        
        try:
            expiry = datetime.fromisoformat(credentials_data['expiry'])
            return datetime.now() >= expiry
        except:
            return True

def handle_oauth_callback():
    """Handle OAuth callback in Streamlit"""
    query_params = st.experimental_get_query_params()
    
    if 'code' in query_params and 'state' in query_params:
        code = query_params['code'][0]
        state = query_params['state'][0]
        
        # Verify state parameter (basic security check)
        if 'oauth_state' not in st.session_state or st.session_state.oauth_state != state:
            st.error("❌ Invalid OAuth state parameter")
            return False
        
        oauth_handler = OAuthHandler()
        credentials = oauth_handler.exchange_code_for_tokens(code, state)
        
        if credentials:
            # Store credentials in session state
            st.session_state.user_credentials = credentials
            st.session_state.user_authenticated = True
            
            # Clear OAuth state
            if 'oauth_state' in st.session_state:
                del st.session_state.oauth_state
            
            st.success(f"✅ Calendar connected successfully for {credentials.get('user_email', 'Unknown user')}!")
            st.rerun()
            return True
        else:
            st.error("❌ Failed to connect calendar")
            return False
    
    return False

def show_connect_calendar_button():
    """Show connect calendar button if user not authenticated"""
    if 'user_authenticated' not in st.session_state or not st.session_state.user_authenticated:
        oauth_handler = OAuthHandler()
        
        st.markdown("### 🔗 Connect Your Google Calendar")
        st.markdown("To use calendar features, please connect your Google Calendar account:")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("🔗 Connect Google Calendar", type="primary"):
                auth_url, state = oauth_handler.get_auth_url()
                if auth_url:
                    # Store state for verification
                    st.session_state.oauth_state = state
                    st.markdown(f"[Click here to authorize with Google]({auth_url})")
                else:
                    st.error("❌ OAuth not configured")
        
        with col2:
            st.info("""
            **What this does:**
            - Connects to your Google Calendar
            - Allows scheduling meetings
            - Sends calendar invitations
            - Reads your upcoming events
            """)
        
        st.markdown("---")

def show_user_info():
    """Show connected user information"""
    if 'user_authenticated' in st.session_state and st.session_state.user_authenticated:
        credentials = st.session_state.user_credentials
        
        st.markdown("### 👤 Connected User")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Email:** {credentials.get('user_email', 'Unknown')}")
            st.markdown(f"**Name:** {credentials.get('user_name', 'Unknown')}")
            st.markdown(f"**Connected:** {credentials.get('connected_at', 'Unknown')}")
        
        with col2:
            if st.button("🔌 Disconnect", type="secondary"):
                # Clear user credentials
                if 'user_credentials' in st.session_state:
                    del st.session_state.user_credentials
                if 'user_authenticated' in st.session_state:
                    del st.session_state.user_authenticated
                st.success("✅ Disconnected successfully!")
                st.rerun()
        
        st.markdown("---")

def get_user_credentials():
    """Get current user credentials, refresh if needed"""
    if 'user_credentials' not in st.session_state:
        return None
    
    credentials = st.session_state.user_credentials
    oauth_handler = OAuthHandler()
    
    # Check if token is expired
    if oauth_handler.is_token_expired(credentials):
        if credentials.get('refresh_token'):
            # Try to refresh the token
            refreshed = oauth_handler.refresh_tokens(credentials['refresh_token'])
            if refreshed:
                # Update credentials
                credentials.update(refreshed)
                st.session_state.user_credentials = credentials
            else:
                # Refresh failed, user needs to reconnect
                st.error("❌ Your session has expired. Please reconnect your calendar.")
                if 'user_credentials' in st.session_state:
                    del st.session_state.user_credentials
                if 'user_authenticated' in st.session_state:
                    del st.session_state.user_authenticated
                return None
        else:
            # No refresh token, user needs to reconnect
            st.error("❌ Your session has expired. Please reconnect your calendar.")
            if 'user_credentials' in st.session_state:
                del st.session_state.user_credentials
            if 'user_authenticated' in st.session_state:
                del st.session_state.user_authenticated
            return None
    
    return credentials

def is_user_authenticated():
    """Check if user is authenticated"""
    return 'user_authenticated' in st.session_state and st.session_state.user_authenticated 