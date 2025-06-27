"""
LLM client abstraction with multiple fallbacks: Groq, Gemini, OpenAI, and Ollama.
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Try to import Groq SDK
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Groq SDK not available. Install with: pip install groq")

# Pricing (as of 2024-06, update as needed)
GROQ_PRICING = {
    'gemma2-9b-it': 0.27,  # $0.27 per 1M tokens (input+output) - PRIMARY
    'llama-3.3-70b-versatile': 0.59,  # $0.59 per 1M tokens (input+output)
    'llama-3.1-8b-instant': 0.27,  # $0.27 per 1M tokens
    'compound-beta': 0.27,  # $0.27 per 1M tokens
    'mixtral-8x7b-32768': 0.7, # $0.70 per 1M tokens (deprecated)
    'gemma-7b-it': 0.27, # $0.27 per 1M tokens
}
OPENAI_PRICING = {
    'gpt-3.5-turbo': 0.5, # $0.50 per 1M tokens
    'gpt-4o': 5.0,       # $5.00 per 1M tokens
    'gpt-4-turbo': 10.0, # $10.00 per 1M tokens
}

class LLMClient:
    """
    LLM client with multiple fallback providers: Groq, Gemini, OpenAI, and Mistral (Ollama).
    Tracks token usage and cost for cloud LLMs.
    """
    
    def __init__(self):
        """Initialize LLM client with configuration for all providers."""
        # Ollama configuration
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'mistral:latest')
        
        # API Keys
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize Groq client if available
        if GROQ_AVAILABLE and self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            self.groq_client = None
        
        # Provider priorities (order of fallback)
        self.providers = ['groq', 'gemini', 'openai', 'ollama']
    
    def get_response(self, prompt: str, model: str = None) -> str:
        """
        Generate a response using multiple fallback providers.
        Returns the first successful response or error message.
        """
        for provider in self.providers:
            try:
                if provider == 'groq' and self.groq_client:
                    response, usage, cost = self._call_groq(prompt, model)
                    self._log_usage('groq', model, usage, cost)
                    if response and response != '[LLM unavailable]':
                        return response
                elif provider == 'gemini' and self.gemini_api_key:
                    response, usage, cost = self._call_gemini(prompt, model)
                    self._log_usage('gemini', model, usage, cost)
                    if response and response != '[LLM unavailable]':
                        return response
                elif provider == 'openai' and self.openai_api_key:
                    response, usage, cost = self._call_openai(prompt, model)
                    self._log_usage('openai', model, usage, cost)
                    if response and response != '[LLM unavailable]':
                        return response
                elif provider == 'ollama':
                    response, usage, cost = self._call_ollama(prompt, model)
                    self._log_usage('ollama', model, usage, cost)
                    if response and response != '[LLM unavailable]':
                        return response
            except Exception as e:
                print(f"Provider {provider} failed: {e}")
                continue
        
        return '[LLM unavailable - all providers failed]'

    def stream_response(self, prompt: str, model: str = None):
        """
        Generate a streaming response. Currently supports Ollama and Groq streaming.
        """
        # Try Groq streaming first
        if self.groq_client:
            try:
                yield from self._stream_groq(prompt, model)
                return
            except Exception as e:
                print(f"Groq streaming failed: {e}")
        
        # Try Ollama streaming
        try:
            yield from self._stream_ollama(prompt, model)
            return
        except Exception:
            pass
        
        # Fallback to non-streaming for other providers
        response = self.get_response(prompt, model)
        yield response

    def _call_groq(self, prompt: str, model: str = None):
        """Call Groq API using official SDK."""
        model = model or 'gemma2-9b-it'
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                stream=False
            )
            
            response = completion.choices[0].message.content.strip()
            usage = {
                'prompt_tokens': completion.usage.prompt_tokens,
                'completion_tokens': completion.usage.completion_tokens,
                'total_tokens': completion.usage.total_tokens
            }
            total_tokens = usage['total_tokens']
            price_per_million = GROQ_PRICING.get(model, 1.0)
            cost = (total_tokens / 1_000_000) * price_per_million
            
            return response, usage, cost
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return '[LLM unavailable]', {}, 0.0

    def _stream_groq(self, prompt: str, model: str = None):
        """Stream response from Groq using official SDK."""
        model = model or 'gemma2-9b-it'
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"Groq streaming error: {e}")
            yield '[LLM unavailable]'

    def _call_gemini(self, prompt: str, model: str = None):
        """Call Google Gemini API."""
        model = model or 'gemini-2.0-flash-exp'
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        params = {'key': self.gemini_api_key}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "topK": 40
            }
        }
        resp = requests.post(url, json=data, params=params, timeout=30)
        usage = {}
        cost = 0.0
        if resp.ok:
            result = resp.json()
            response = result['candidates'][0]['content']['parts'][0]['text'].strip()
            # Estimate tokens (very rough)
            total_tokens = len(prompt.split()) + len(response.split())
            usage = {'total_tokens': total_tokens}
            # Gemini 2.0 pricing: $0.15 per 1M tokens (estimate)
            cost = (total_tokens / 1_000_000) * 0.15
            return response, usage, cost
        return '[LLM unavailable]', usage, cost

    def _call_openai(self, prompt: str, model: str = None):
        """Call OpenAI API."""
        model = model or 'gpt-3.5-turbo'
        headers = {"Authorization": f"Bearer {self.openai_api_key}"}
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", 
                           json=data, headers=headers, timeout=30)
        if resp.ok:
            result = resp.json()
            usage = result.get('usage', {})
            total_tokens = usage.get('total_tokens', 0)
            price_per_million = OPENAI_PRICING.get(model, 1.0)
            cost = (total_tokens / 1_000_000) * price_per_million
            return result['choices'][0]['message']['content'].strip(), usage, cost
        return '[LLM unavailable]', {}, 0.0

    def _call_ollama(self, prompt: str, model: str = None):
        """Call Ollama API."""
        model = model or self.ollama_model
        try:
            resp = requests.post(f"{self.ollama_host}/api/generate", json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }, timeout=30)
            if resp.ok:
                result = resp.json()
                response = result.get('response', '').strip()
                # Estimate tokens (very rough)
                total_tokens = len(prompt.split()) + len(response.split())
                usage = {'total_tokens': total_tokens}
                cost = 0.0  # Local model, no cost
                return response, usage, cost
        except Exception:
            pass
        return '[LLM unavailable]', {}, 0.0

    def _stream_ollama(self, prompt: str, model: str = None):
        """Stream response from Ollama."""
        model = model or self.ollama_model
        try:
            resp = requests.post(f"{self.ollama_host}/api/generate", json={
                "model": model,
                "prompt": prompt,
                "stream": True
            }, stream=True, timeout=30)
            for line in resp.iter_lines():
                if line:
                    try:
                        chunk = line.decode('utf-8')
                        yield chunk
                    except Exception:
                        continue
        except Exception:
            yield '[LLM unavailable]'

    def _log_usage(self, provider, model, usage, cost):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider,
            'model': model,
            'usage': usage,
            'cost_usd': cost
        }
        try:
            with open('llm_usage.log', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to log LLM usage: {e}")

# Legacy function for backward compatibility
def generate_response(prompt, model=None, stream=False):
    """
    Legacy function for backward compatibility.
    Returns a string for non-streaming, and a string (joined) for streaming.
    """
    client = LLMClient()
    if stream:
        return ''.join(list(client.stream_response(prompt, model)))
    else:
        return client.get_response(prompt, model) 