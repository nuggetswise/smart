#!/bin/bash

# SmartDesk AI - Production Deployment Script
# This script helps set up SmartDesk AI for production deployment

set -e

echo "🚀 SmartDesk AI - Production Deployment Setup"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the SmartDeskAI project root directory"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p ~/.credentials

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
    echo "   Then edit .env with your API keys and credentials"
    echo ""
    echo "🔑 Required environment variables:"
    echo "   - At least one LLM provider (GROQ_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY)"
    echo "   - Google Calendar credentials (GOOGLE_CALENDAR_CLIENT_ID, GOOGLE_CALENDAR_CLIENT_SECRET)"
    echo "   - Security keys (SECRET_KEY, SMARTDESK_AI_API_KEY)"
    echo ""
    read -p "Press Enter to continue after setting up .env file..."
fi

# Check for credentials.json
if [ ! -f "credentials.json" ]; then
    echo "⚠️  credentials.json not found!"
    echo "📝 Please download Google Calendar OAuth credentials:"
    echo "   1. Go to https://console.cloud.google.com/"
    echo "   2. Create a project and enable Google Calendar API"
    echo "   3. Create OAuth 2.0 credentials (Web application type)"
    echo "   4. Add redirect URIs: http://localhost:8508/_stcore/authorize"
    echo "   5. Download as credentials.json and place in project root"
    echo ""
    read -p "Press Enter to continue after adding credentials.json..."
fi

# Generate secret key if not set
if [ -f ".env" ] && ! grep -q "SECRET_KEY=your_secret_key_here" .env; then
    echo "✅ SECRET_KEY already configured"
else
    echo "🔐 Generating SECRET_KEY..."
    SECRET_KEY=$(openssl rand -hex 32)
    echo "Generated SECRET_KEY: $SECRET_KEY"
    echo "Please add this to your .env file: SECRET_KEY=$SECRET_KEY"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check for required system dependencies
echo "🔍 Checking system dependencies..."

# Check for Tesseract (OCR)
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract not found. Install for OCR functionality:"
    echo "   macOS: brew install tesseract"
    echo "   Ubuntu: sudo apt-get install tesseract-ocr"
    echo "   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

# Check for Ollama (optional)
if ! command -v ollama &> /dev/null; then
    echo "ℹ️  Ollama not found. Install for local LLM (optional):"
    echo "   Visit https://ollama.com/ for installation instructions"
fi

# Test the application
echo "🧪 Testing application setup..."

# Test Python imports
python -c "
import sys
try:
    from core.llm_client import LLMClient
    from core.tools.calendar_tool import CalendarTool
    from core.agents.calendar_agent import CalendarAgent
    print('✅ All core modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Test environment variables
if [ -f ".env" ]; then
    echo "🔧 Testing environment configuration..."
    python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = ['GROQ_API_KEY', 'GEMINI_API_KEY', 'OPENAI_API_KEY']
found_vars = [var for var in required_vars if os.getenv(var)]
if found_vars:
    print(f'✅ LLM provider configured: {found_vars[0]}')
else:
    print('❌ No LLM provider configured. Please set at least one of: GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY')
"
fi

# Create production configuration
echo "⚙️  Creating production configuration..."

# Create logs directory with proper permissions
mkdir -p logs
chmod 755 logs

# Create a production startup script
cat > start_production.sh << 'EOF'
#!/bin/bash

# SmartDesk AI - Production Startup Script

# Set production environment
export DEBUG=false
export TEST_MODE=false
export LOG_LEVEL=INFO

# Start the application
echo "🚀 Starting SmartDesk AI in production mode..."
streamlit run main.py \
    --server.port=8508 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --logger.level=info
EOF

chmod +x start_production.sh

# Create systemd service file (optional)
cat > smartdesk-ai.service << 'EOF'
[Unit]
Description=SmartDesk AI
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/SmartDeskAI
Environment=PATH=/path/to/SmartDeskAI/.venv/bin
ExecStart=/path/to/SmartDeskAI/.venv/bin/streamlit run main.py --server.port=8508 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "📋 Production setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure your .env file with API keys"
echo "2. Add Google Calendar credentials.json"
echo "3. Test the application: streamlit run main.py"
echo "4. For production: ./start_production.sh"
echo ""
echo "📊 Monitoring:"
echo "- Application logs: logs/smartdesk_ai.log"
echo "- LLM usage: llm_usage.log"
echo "- Calendar notifications: calendar_notifications.json"
echo ""
echo "🔧 Optional:"
echo "- Edit smartdesk-ai.service for systemd deployment"
echo "- Configure reverse proxy (nginx) for HTTPS"
echo "- Set up monitoring and alerting"
echo ""
echo "✅ SmartDesk AI is ready for production deployment!" 