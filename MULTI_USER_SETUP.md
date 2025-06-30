
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
