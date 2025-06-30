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
        
        # Initialize Groq client if available and test the API key
        self.groq_client = None
        self.groq_api_key_valid = False
        if GROQ_AVAILABLE and self.groq_api_key:
            try:
                # Test the API key by making a simple request
                test_client = Groq(api_key=self.groq_api_key)
                # Try a minimal test call
                test_response = test_client.chat.completions.create(
                    model="gemma2-9b-it",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                # If we get here, the API key is valid
                self.groq_client = test_client
                self.groq_api_key_valid = True
                print("✅ Groq API key validated successfully")
            except Exception as e:
                print(f"❌ Groq API key validation failed: {e}")
                self.groq_client = None
                self.groq_api_key_valid = False
        
        # Provider priorities (order of fallback) - include Groq even if validation failed
        self.providers = []
        if self.groq_api_key:  # Include Groq if API key exists, even if validation failed
            self.providers.append('groq')
        if self.gemini_api_key:
            self.providers.append('gemini')
        if self.openai_api_key:
            self.providers.append('openai')
        self.providers.append('ollama')  # Always include Ollama as fallback
        
        print(f"🔧 Available LLM providers: {self.providers}")
    
    def get_response(self, prompt: str, model: str = None) -> str:
        """
        Generate a response using multiple fallback providers.
        Returns the first successful response or error message.
        """
        print(f"🤖 Attempting to get response from providers: {self.providers}")
        
        # Smart model selection - if model is a Groq model but Groq is not available, use appropriate default
        if model and model.startswith(('gemma', 'llama')) and 'groq' not in self.providers:
            if 'gemini' in self.providers:
                model = 'gemma-3n-e2b-it'
                print(f"🔄 Switching from Groq model to Gemini model: {model}")
            elif 'openai' in self.providers:
                model = 'gpt-3.5-turbo'
                print(f"🔄 Switching from Groq model to OpenAI model: {model}")
        
        # Track failed providers for better error reporting
        failed_providers = []
        
        for provider in self.providers:
            try:
                print(f"🔄 Trying provider: {provider}")
                
                # Add retry logic for each provider
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        if provider == 'groq' and self.groq_api_key:
                            # Initialize Groq client on-demand if not already done
                            if not self.groq_client and self.groq_api_key:
                                try:
                                    self.groq_client = Groq(api_key=self.groq_api_key)
                                    self.groq_api_key_valid = True
                                except Exception as e:
                                    print(f"❌ Failed to initialize Groq client: {e}")
                                    break
                            
                            if self.groq_client:
                                response, usage, cost = self._call_groq(prompt, model)
                                self._log_usage('groq', model, usage, cost)
                                if response and response != '[LLM unavailable]':
                                    print(f"✅ Groq response successful")
                                    return response
                                else:
                                    print(f"❌ Groq returned unavailable response")
                                    break
                            else:
                                print(f"❌ Groq client not available")
                                break
                        elif provider == 'gemini' and self.gemini_api_key:
                            response, usage, cost = self._call_gemini(prompt, model)
                            self._log_usage('gemini', model, usage, cost)
                            if response and response != '[LLM unavailable]':
                                print(f"✅ Gemini response successful")
                                return response
                            else:
                                print(f"❌ Gemini returned unavailable response")
                                break
                        elif provider == 'openai' and self.openai_api_key:
                            response, usage, cost = self._call_openai(prompt, model)
                            self._log_usage('openai', model, usage, cost)
                            if response and response != '[LLM unavailable]':
                                print(f"✅ OpenAI response successful")
                                return response
                            else:
                                print(f"❌ OpenAI returned unavailable response")
                                break
                        elif provider == 'ollama':
                            response, usage, cost = self._call_ollama(prompt, model)
                            self._log_usage('ollama', model, usage, cost)
                            if response and response != '[LLM unavailable]':
                                print(f"✅ Ollama response successful")
                                return response
                            else:
                                print(f"❌ Ollama returned unavailable response")
                                break
                        
                        # If we get here, the provider worked but returned unavailable
                        break
                        
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"⚠️ Provider {provider} attempt {attempt + 1} failed: {e}. Retrying...")
                            import time
                            time.sleep(1)  # Brief delay before retry
                        else:
                            raise e
                            
            except Exception as e:
                error_msg = f"Provider {provider} failed: {str(e)}"
                print(f"❌ {error_msg}")
                failed_providers.append(error_msg)
                continue
        
        # If we get here, all providers failed
        error_summary = f"All LLM providers failed:\n" + "\n".join(failed_providers)
        print(f"❌ {error_summary}")
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
        # Use Gemini-specific model names
        if model and model.startswith('gemma'):  # If it's a Groq model, use Gemini default
            model = 'gemma-3n-e2b-it'
        model = model or 'gemma-3n-e2b-it'
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
        try:
            # Increase timeout and add retry logic
            resp = requests.post(url, json=data, params=params, timeout=60)
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
            else:
                print(f"❌ Gemini API error: {resp.status_code} - {resp.text}")
                return '[LLM unavailable]', usage, cost
        except requests.exceptions.Timeout:
            print(f"❌ Gemini API timeout - request took too long")
            return '[LLM unavailable]', {}, 0.0
        except requests.exceptions.ConnectionError:
            print(f"❌ Gemini API connection error - network issue")
            return '[LLM unavailable]', {}, 0.0
        except Exception as e:
            print(f"❌ Gemini API exception: {e}")
            return '[LLM unavailable]', {}, 0.0

    def _call_openai(self, prompt: str, model: str = None):
        """Call OpenAI API."""
        # Use OpenAI-specific model names
        if model and (model.startswith('gemma') or model.startswith('llama')):  # If it's a Groq model, use OpenAI default
            model = 'gpt-3.5-turbo'
        model = model or 'gpt-3.5-turbo'
        headers = {"Authorization": f"Bearer {self.openai_api_key}"}
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            # Increase timeout and add retry logic
            resp = requests.post("https://api.openai.com/v1/chat/completions", 
                               json=data, headers=headers, timeout=60)
            if resp.ok:
                result = resp.json()
                usage = result.get('usage', {})
                total_tokens = usage.get('total_tokens', 0)
                price_per_million = OPENAI_PRICING.get(model, 1.0)
                cost = (total_tokens / 1_000_000) * price_per_million
                return result['choices'][0]['message']['content'].strip(), usage, cost
            else:
                print(f"❌ OpenAI API error: {resp.status_code} - {resp.text}")
                return '[LLM unavailable]', {}, 0.0
        except requests.exceptions.Timeout:
            print(f"❌ OpenAI API timeout - request took too long")
            return '[LLM unavailable]', {}, 0.0
        except requests.exceptions.ConnectionError:
            print(f"❌ OpenAI API connection error - network issue")
            return '[LLM unavailable]', {}, 0.0
        except Exception as e:
            print(f"❌ OpenAI API exception: {e}")
            return '[LLM unavailable]', {}, 0.0

    def _call_ollama(self, prompt: str, model: str = None):
        """Call Ollama API."""
        # Use Ollama-specific model names
        if model and (model.startswith('gemma') or model.startswith('llama')):  # If it's a Groq model, use Ollama default
            model = self.ollama_model
        model = model or self.ollama_model
        try:
            # Increase timeout for local model
            resp = requests.post(f"{self.ollama_host}/api/generate", json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }, timeout=120)  # Longer timeout for local model
            if resp.ok:
                result = resp.json()
                response = result.get('response', '').strip()
                # Estimate tokens (very rough)
                total_tokens = len(prompt.split()) + len(response.split())
                usage = {'total_tokens': total_tokens}
                cost = 0.0  # Local model, no cost
                return response, usage, cost
            else:
                print(f"❌ Ollama API error: {resp.status_code} - {resp.text}")
                return '[LLM unavailable]', {}, 0.0
        except requests.exceptions.Timeout:
            print(f"❌ Ollama API timeout - local model may be overloaded")
            return '[LLM unavailable]', {}, 0.0
        except requests.exceptions.ConnectionError:
            print(f"❌ Ollama API connection error - Ollama may not be running")
            return '[LLM unavailable]', {}, 0.0
        except Exception as e:
            print(f"❌ Ollama API exception: {e}")
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