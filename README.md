# SmartDesk AI

A production-ready productivity assistant built with Streamlit, featuring AI-powered calendar management, document processing, and intelligent task management.

## 🚀 Features

- **🤖 AI-Powered Calendar Agent**: Proactive meeting notifications with AI insights and preparation suggestions
- **📷 Document Processing**: OCR for images, PDF text extraction, and intelligent content analysis
- **🔍 Web Search & Research**: Powered by Serper.dev or DuckDuckGo with AI summarization
- **💬 Intelligent Chat**: Persistent memory-enabled assistant with multiple LLM providers
- **📅 Google Calendar Integration**: Real-time calendar monitoring and smart notifications
- **🔄 Proactive Agents**: Background monitoring for meetings and productivity insights
- **💾 Local Data Storage**: All data stored locally with TinyDB/SQLite

## 🛠️ Production Setup

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd SmartDeskAI
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

**Required Environment Variables:**

#### LLM Configuration (Choose at least one)
```bash
# Groq API (Recommended - Fast and cost-effective)
GROQ_API_KEY=your_groq_api_key_here

# Google Gemini API (Alternative - Good for cost)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API (Alternative - Most capable but expensive)
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (Local LLM - Optional)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:latest
```

#### Google Calendar Integration (Required for calendar features)
```bash
# Download from: https://console.cloud.google.com/apis/credentials
GOOGLE_CALENDAR_CLIENT_ID=your_google_client_id_here
GOOGLE_CALENDAR_CLIENT_SECRET=your_google_client_secret_here
```

#### Web Search (Optional)
```bash
# Serper.dev API for enhanced web search
SERPER_API_KEY=your_serper_api_key_here
```

#### Security (Required for production)
```bash
# Generate with: openssl rand -hex 32
SECRET_KEY=your_secret_key_here

# API key for webhook authentication
SMARTDESK_AI_API_KEY=your_api_key_here
```

### 3. Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Web application type)
5. Add authorized redirect URIs:
   - `http://localhost:8508/_stcore/authorize`
   - `http://localhost:8508/`
6. Download credentials and save as `credentials.json` in project root

### 4. Run the Application

```bash
streamlit run main.py
```

Access the app at: http://localhost:8508

## 🔧 API Key Setup Guide

### Groq API (Recommended)
1. Visit [console.groq.com](https://console.groq.com/)
2. Sign up for free account
3. Generate API key
4. Add to `.env`: `GROQ_API_KEY=your_key_here`

### Google Gemini API
1. Visit [makersuite.google.com](https://makersuite.google.com/)
2. Create API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`

### Serper.dev (Web Search)
1. Visit [serper.dev](https://serper.dev/)
2. Sign up and get API key
3. Add to `.env`: `SERPER_API_KEY=your_key_here`

## 📁 Project Structure

```
SmartDeskAI/
├── main.py                 # Main Streamlit application
├── app.py                  # Enhanced UI components
├── core/
│   ├── agents/            # AI agents (calendar, etc.)
│   ├── tools/             # Core tools (OCR, calendar, search)
│   ├── llm_client.py      # Multi-provider LLM client
│   ├── chat_router.py     # Message routing and processing
│   └── memory/            # Long-term memory system
├── ui/                    # UI components
├── utils/                 # Utility functions
├── components/            # Reusable UI components
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🚀 Production Deployment

### Environment Variables for Production

Set these in your production environment:

```bash
# Security
DEBUG=false
TEST_MODE=false
SECRET_KEY=your_strong_secret_key

# Performance
LOG_LEVEL=INFO
CACHE_TIMEOUT=3600
MAX_UPLOAD_SIZE=10485760

# Application
APP_PORT=8508
APP_HOST=0.0.0.0
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8508

CMD ["streamlit", "run", "main.py", "--server.port=8508", "--server.address=0.0.0.0"]
```

## 🔍 Usage

### Calendar Features
- **Proactive Notifications**: Get notified 15 minutes before meetings
- **AI Insights**: Receive AI-powered meeting preparation suggestions
- **Calendar Commands**: Use `/calendar` to check upcoming events

### Document Processing
- **Image OCR**: Upload handwritten notes or whiteboard images
- **PDF Analysis**: Extract and analyze PDF content
- **AI Summarization**: Get intelligent summaries of documents

### Web Research
- **Smart Search**: Use `/search [query]` for web research
- **AI Summarization**: Get summarized results with citations

### Chat Assistant
- **Persistent Memory**: Conversations are remembered across sessions
- **Context Awareness**: AI understands conversation history
- **Multi-Modal**: Handle text, images, and documents

## 🛡️ Security Notes

- ✅ `credentials.json` is automatically ignored by git
- ✅ All sensitive data stored locally
- ✅ Environment variables for API keys
- ✅ No cloud authentication required
- ✅ Local data storage only

## 🔧 Troubleshooting

### Common Issues

**Calendar not connecting?**
- Ensure `credentials.json` is in project root
- Check OAuth redirect URIs match your app URL
- Verify Google Calendar API is enabled

**LLM not responding?**
- Check API keys in `.env` file
- Verify at least one LLM provider is configured
- Check network connectivity

**OCR not working?**
- Install Tesseract: `brew install tesseract` (macOS)
- Ensure EasyOCR is installed: `pip install easyocr`

**App not starting?**
- Check all required environment variables are set
- Verify Python dependencies are installed
- Check port 8508 is available

## 📊 Monitoring

### Logs
- Application logs: `logs/smartdesk_ai.log`
- LLM usage logs: `llm_usage.log`
- Calendar notifications: `calendar_notifications.json`

### Health Checks
- App status: http://localhost:8508
- Calendar status: Use `/calendar-agent` command
- LLM status: Check response to simple queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**SmartDesk AI** - Your intelligent productivity companion 🚀 