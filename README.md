# SmartDesk AI

A multifunctional productivity assistant built with Streamlit, inspired by Nuggetwise's clean, modern UI.

---

## 🚀 Features

- **Image/Note → Action Items**: Upload handwritten notes or whiteboard images, extract text (OCR), and summarize into actionable tasks using a local LLM (Ollama) or Groq API.
- **Chat Assistant**: Chat with a persistent, memory-enabled assistant. System prompt and tone are configurable.
- **Web Search + Deep Research**: Search the web (Serper.dev or DuckDuckGo), scrape top links, and get LLM-powered summaries with citations.
- **Calendar Agent**: Connect Google Calendar, view upcoming events, and get smart suggestions for meetings.
- **Persistent Storage**: All data (tasks, chat, preferences) is stored locally in `~/.smartdesk_ai/`.
- **Nuggetwise-inspired UI**: Consistent, beautiful design across all pages.

---

## 🛠️ Setup

### 1. Clone the Repo
```bash
git clone <your-repo-url>
cd SmartDeskAI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
- Copy `.env.example` to `.env` and fill in your API keys and credentials:

```bash
cp .env.example .env
```

- Edit `.env` with your favorite editor and set:
  - Ollama (local LLM) or Groq API key
  - Serper.dev or DuckDuckGo API key
  - Google Calendar OAuth credentials
  - System prompt (optional)

### 4. Run the App
```bash
streamlit run main.py
```

---

## 📦 Folder Structure

```
SmartDeskAI/
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── style_guide.md
├── /pages/
├── /components/
├── /utils/
```

---

## ⚡ Usage
- **Login**: Start with your username and password (no cloud auth, local only).
- **Onboarding**: Complete the multi-step wizard to personalize your experience.
- **Image/Note → Action Items**: Upload an image, extract text, and generate action items.
- **Chat Assistant**: Chat with memory and persistent context.
- **Web Research**: Enter a topic, get summarized research with citations.
- **Calendar Agent**: Connect Google Calendar and get smart meeting suggestions.

---

## 🧩 Local & Offline Notes
- **LLM**: Uses Ollama (local) if available, otherwise Groq API (free tier).
- **OCR**: Uses pytesseract (local) with EasyOCR fallback.
- **All data is stored locally** in `~/.smartdesk_ai/` (TinyDB JSON or SQLite).
- **No paid OpenAI required.**

---

## ❓ Troubleshooting & FAQ

- **Ollama not running?**
  - Download and start Ollama from [ollama.com](https://ollama.com/).
  - Make sure the model (e.g., `mistral`) is downloaded: `ollama run mistral`.
- **Groq API not working?**
  - Get a free API key from [groq.com](https://console.groq.com/).
- **Google Calendar not connecting?**
  - Ensure your OAuth credentials are correct in `.env`.
  - The redirect URI should match your Streamlit app URL (default: `http://localhost:8501`).
- **OCR errors?**
  - Make sure Tesseract is installed (`brew install tesseract` on macOS).
- **Where is my data?**
  - All user data is in `~/.smartdesk_ai/`.

---

## 🖌️ Style Guide
See `style_guide.md` for all UI/UX rules and design tokens.

---

## 📬 Feedback & Contributions
Pull requests and issues are welcome! 