#!/usr/bin/env python3
"""
Multi-User Calendar Integration Setup Guide
"""
import os
import json
from datetime import datetime

def create_oauth_setup_guide():
    """Create a comprehensive guide for multi-user OAuth setup"""
    
    guide = """
# 🔐 Multi-User Calendar Integration Setup

## Current Limitation
The app currently uses a single `credentials.json` file, making it only usable by one user.

## 🚀 Solution: OAuth2 Flow

### Step 1: Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8501/oauth/callback`
     - `https://your-domain.com/oauth/callback` (for production)

### Step 2: Environment Variables
Create a `.env` file:
```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8501/oauth/callback
```

### Step 3: User Authentication Flow
1. User visits the app
2. Clicks "Connect Calendar" button
3. Redirected to Google OAuth consent screen
4. User grants permissions
5. Redirected back with authorization code
6. App exchanges code for access/refresh tokens
7. Tokens stored securely (database/encrypted file)
8. User can now use calendar features

### Step 4: Database Schema (Optional)
```sql
CREATE TABLE user_calendars (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 Alternative: Manual Setup Per User

### For Development/Testing:
1. Each user creates their own `credentials.json`
2. Users place their credentials in a user-specific folder
3. App detects and loads user-specific credentials

### File Structure:
```
SmartDeskAI/
├── users/
│   ├── user1/
│   │   ├── credentials.json
│   │   └── token.json
│   ├── user2/
│   │   ├── credentials.json
│   │   └── token.json
│   └── ...
├── core/
└── ...
```

## 🛠️ Implementation Steps

### 1. Create OAuth Handler
```python
# oauth_handler.py
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

def handle_oauth_flow():
    # OAuth flow implementation
    pass
```

### 2. Update Calendar Tool
```python
# calendar_tool.py
class CalendarTool:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.credentials = self._load_user_credentials()
    
    def _load_user_credentials(self):
        # Load user-specific credentials
        pass
```

### 3. Add User Management
```python
# user_manager.py
class UserManager:
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id, credentials):
        # Add user with their credentials
        pass
    
    def get_user_calendar(self, user_id):
        # Get calendar tool for specific user
        pass
```

## 🔒 Security Considerations

### Token Storage:
- **Development**: Encrypted local files
- **Production**: Secure database with encryption
- **Never**: Store tokens in plain text

### Access Control:
- Validate user permissions
- Implement session management
- Add rate limiting

### Data Privacy:
- Clear user data on request
- Implement data retention policies
- Follow GDPR/privacy regulations

## 📋 Deployment Options

### 1. Local Development
- Each user runs their own instance
- Uses local credentials files

### 2. Shared Server
- OAuth flow for user authentication
- Database storage for tokens
- Multi-tenant architecture

### 3. Cloud Deployment
- OAuth flow
- Cloud database (PostgreSQL, MongoDB)
- Containerized deployment (Docker)

## 🎯 Quick Start for New Users

### Option A: OAuth (Recommended)
1. User visits app
2. Clicks "Connect Calendar"
3. Authorizes with Google
4. Ready to use!

### Option B: Manual Setup
1. User downloads credentials template
2. Follows Google Calendar API setup guide
3. Uploads credentials to app
4. Ready to use!

## 📝 Next Steps

1. **Choose approach**: OAuth vs Manual
2. **Implement authentication flow**
3. **Update calendar tool for multi-user**
4. **Add user management interface**
5. **Test with multiple users**
6. **Deploy and monitor**

## 🔗 Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Streamlit OAuth Examples](https://github.com/streamlit/streamlit-example-oauth)
"""
    
    # Save guide to file
    with open('MULTI_USER_SETUP.md', 'w') as f:
        f.write(guide)
    
    print("✅ Multi-user setup guide created: MULTI_USER_SETUP.md")
    return guide

def create_oauth_implementation():
    """Create a basic OAuth implementation template"""
    
    oauth_code = '''
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
'''
    
    # Save OAuth implementation
    with open('oauth_handler.py', 'w') as f:
        f.write(oauth_code)
    
    print("✅ OAuth implementation template created: oauth_handler.py")
    return oauth_code

if __name__ == "__main__":
    print("🚀 Creating Multi-User Calendar Integration Setup...")
    create_oauth_setup_guide()
    create_oauth_implementation()
    print("\n📋 Files created:")
    print("- MULTI_USER_SETUP.md (Complete setup guide)")
    print("- oauth_handler.py (OAuth implementation template)")
    print("\n🎯 Next steps:")
    print("1. Read MULTI_USER_SETUP.md for detailed instructions")
    print("2. Choose your preferred approach (OAuth or Manual)")
    print("3. Implement the chosen solution")
    print("4. Test with multiple users") 