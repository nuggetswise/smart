import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT', 'You are SmartDesk AI, a helpful productivity assistant.')


def summarize_action_items(text):
    prompt = f"""
{SYSTEM_PROMPT}

Extract actionable tasks from the following notes. Return a bullet list of action items, each with optional priority, due date, and tags if possible.

Notes:
{text}
"""
    # Prefer Ollama if running locally
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        if resp.ok:
            return resp.json().get('response', '').strip()
    except Exception:
        pass
    # Fallback to Groq API
    if GROQ_API_KEY:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers, timeout=30)
        if resp.ok:
            return resp.json()['choices'][0]['message']['content'].strip()
    return "[LLM unavailable]" 