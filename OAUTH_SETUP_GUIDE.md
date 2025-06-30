# 🔐 OAuth2 Setup Guide for SmartDesk AI

## 🚀 Quick Start

### Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Google Calendar API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Application type: **Web application**
   - Name: `SmartDesk AI`
   - Authorized redirect URIs:
     - `http://localhost:8501/oauth/callback` (for development)
     - `https://your-domain.com/oauth/callback` (for production)

4. **Copy Credentials**
   - Copy the **Client ID** and **Client Secret**
   - Keep these secure!

### Step 2: Environment Configuration

1. **Create `.env` file**
   ```bash
   cp env_template.txt .env
   ```

2. **Edit `.env` file**
   ```env
   GOOGLE_CLIENT_ID=your_actual_client_id_here
   GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:8501/oauth/callback
   
   # Your existing LLM API keys
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the App

```bash
streamlit run streamlit_app.py
```

## 🎯 How It Works

### User Flow:
1. **User visits app** → Sees "Connect Google Calendar" button
2. **Clicks connect** → Redirected to Google OAuth consent screen
3. **Authorizes** → Google redirects back with authorization code
4. **App exchanges code** → Gets access/refresh tokens
5. **User authenticated** → Can now use calendar features

### Features:
- ✅ **Multi-user support** - Each user connects their own calendar
- ✅ **Secure token storage** - Tokens stored in session state
- ✅ **Automatic refresh** - Tokens refresh automatically when expired
- ✅ **Easy disconnect** - Users can disconnect anytime
- ✅ **Fallback support** - Still works with file-based credentials

## 🔒 Security Features

- **State parameter** - Prevents CSRF attacks
- **Secure token handling** - Tokens stored securely
- **Automatic token refresh** - Handles expired tokens
- **User isolation** - Each user only sees their own calendar
- **Easy logout** - Users can disconnect securely

## 🛠️ Troubleshooting

### Common Issues:

1. **"OAuth not configured"**
   - Check your `.env` file has correct credentials
   - Verify Google Cloud Console setup

2. **"Invalid redirect URI"**
   - Make sure redirect URI in Google Console matches your `.env`
   - For development: `http://localhost:8501/oauth/callback`

3. **"Calendar not available"**
   - User needs to connect their calendar first
   - Check if OAuth flow completed successfully

4. **"Token expired"**
   - App will automatically refresh tokens
   - If refresh fails, user needs to reconnect

### Debug Mode:
```bash
# Run with debug logging
streamlit run streamlit_app.py --logger.level=debug
```

## 📋 Production Deployment

### For Production:
1. **Update redirect URI** in Google Console to your domain
2. **Use HTTPS** - OAuth requires secure connections
3. **Database storage** - Store tokens in secure database
4. **Environment variables** - Use proper secret management
5. **Rate limiting** - Implement API rate limiting

### Example Production `.env`:
```env
GOOGLE_CLIENT_ID=your_production_client_id
GOOGLE_CLIENT_SECRET=your_production_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/oauth/callback
```

## 🎉 Success!

Once configured:
- Users can connect their calendars with one click
- Each user gets their own calendar access
- No more manual credential setup
- Secure and user-friendly experience

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify Google Cloud Console setup
3. Check environment variables
4. Review Streamlit logs for errors 