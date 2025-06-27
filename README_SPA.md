# SmartDeskAI: Assistant-First SPA

A single-page, agentic productivity assistant inspired by ChatGPT and Nuggetwise. All user interaction happens through a unified chat interface, with agent tools for OCR, calendar, web search, and summarization.

---

## 🚀 Features

- **Unified Chat Interface**: All user input (text, file, image) is handled in a single persistent chat thread.
- **Agentic Routing**: Chat input is routed to the correct tool (OCR, calendar, web search, summarizer, or LLM) via a central router.
- **Proactive Calendar Agent**: Background polling for upcoming events, with system reminders in the chat.
- **Web Search Mode**: User-controlled toggle for on-demand web search and summarization.
- **OCR**: Extract text from images using pytesseract/EasyOCR.
- **Long-Form Summarization**: Summarize notes, documents, or web content.
- **Persistent Memory**: All chat and context stored in TinyDB/SQLite, with pruning/TTL.
- **Persona Injection**: System prompt and memory limit loaded from `persona_config.json`.
- **Nuggetwise-Inspired UI**: Clean, modern, segmented card layout with rounded corners, shadows, and proper spacing.

---

## 📦 Project Structure

```
SmartDeskAI/
├── app.py                     # Single-page Streamlit entrypoint
├── core/
│   ├── chat_router.py         # Routes all input to tools or LLM
│   ├── tools/
│   │   ├── ocr_tool.py
│   │   ├── calendar_tool.py
│   │   ├── websearch_tool.py
│   │   └── summarizer.py
│   ├── llm_client.py          # Abstraction for Ollama/Groq
│   ├── memory/
│   │   ├── long_term_memory.py
│   │   └── persona_config.json
├── ui/
│   ├── chat_interface.py      # Persistent chat thread UI
│   └── upload_handler.py      # Handles file/image inputs
├── .env
├── requirements.txt
├── README_SPA.md
```

---

## 🛠️ Setup

1. **Clone the repo**
   ```bash
   git clone <your-repo-url>
   cd SmartDeskAI
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment**
   - Fill in `.env` with your API keys (Groq, Serper, etc.)
   - Run `nomic login` if using nomic-embed-text
4. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## 🧠 Agentic Routing
- All chat input is routed via `core/chat_router.py`.
- Tools are called as needed (OCR, calendar, web search, summarizer, LLM).
- Calendar agent polls in the background and posts reminders as system messages.
- Web search mode can be toggled by the user.

---

## 🎨 Style Guide Compliance
- White background, segmented card layout
- Rounded message bubbles (12–16 px radius)
- Violet primary buttons, light grey secondary
- Consistent padding, margin, and soft shadows
- No sidebar; full-width centered layout

---

## 📝 Memory & Persona
- Persistent chat memory with pruning/TTL (configurable)
- Persona/system prompt loaded from `persona_config.json`

---

## 📬 Feedback & Contributions
Pull requests and issues are welcome! 


Understood! Here’s how I’ll proceed to deliver a **fully functional, agentic SPA** for SmartDeskAI:

---

## 🟣 Implementation Plan (Full Feature Build)

### 1. **chat_router.py**
- Implement `route_input(message, files=None)`:
  - Detect intent (calendar, web search, OCR, summarization, or general chat)
  - Route to the correct tool or LLM
  - Return formatted assistant reply

### 2. **llm_client.py**
- Implement `generate_response(prompt, model='llama3:8b')`:
  - Call Ollama (local) or Groq (cloud) for chat/summarization
  - Support streaming for large responses

### 3. **tools/**
- **ocr_tool.py:** Use pytesseract/EasyOCR to extract text from images
- **calendar_tool.py:** Use `gcsa` to poll Google Calendar, monitor events, and push reminders
- **websearch_tool.py:** Use Serper.dev or DuckDuckGo for search, summarize with LLM
- **summarizer.py:** Use LLM for long-form summarization

### 4. **memory/long_term_memory.py**
- Implement persistent chat memory (TinyDB/SQLite)
- Add TTL/pruning based on `persona_config.json`

### 5. **ui/chat_interface.py**
- Render a single chat thread (markdown, streaming, system messages)
- Support user text input and file/image upload (via `upload_handler.py`)
- Show reminders, tool status, and search mode notifications

### 6. **ui/upload_handler.py**
- Handle file/image uploads and pass to OCR tool

### 7. **Style Guide**
- Ensure all UI matches Nuggetwise style (rounded cards, segmented layout, no sidebar, etc.)

---

**I will now begin implementing each feature, integrating all components into a seamless, agentic chat experience.**

You’ll receive updates as each major feature is completed. If you want to review or adjust any part of the implementation, just let me know—otherwise, I’ll proceed with the full build-out!