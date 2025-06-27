"""
Web search tool using Serper.dev or DuckDuckGo, with LLM summarization.
"""
import os
from duckduckgo_search import DDGS
import requests
from core.llm_client import generate_response
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

class WebSearchTool:
    """
    Web search tool using Serper.dev or DuckDuckGo, with LLM summarization.
    """
    def __init__(self):
        self.serper_api_key = SERPER_API_KEY
    
    def search(self, query: str) -> str:
        """
        Search the web and return a summarized markdown response.
        """
        results = []
        if self.serper_api_key:
            resp = requests.post('https://google.serper.dev/search', json={'q': query}, headers={'X-API-KEY': self.serper_api_key})
            if resp.ok:
                results = resp.json().get('organic', [])
        else:
            with DDGS() as ddgs:
                for r in ddgs.text(query):
                    if 'href' in r and 'body' in r:
                        results.append({'link': r['href'], 'snippet': r['body']})
                    if len(results) >= 3:
                        break
        # Build context for LLM
        context = '\n'.join([f"{r.get('snippet','')} ({r.get('link','')})" for r in results])
        prompt = f"""
You are a research assistant. Summarize the following web results for the user. Include hyperlinks in markdown.

Web results:
{context}

Summary:
"""
        summary = generate_response(prompt, stream=False)
        return summary

def search_and_summarize(query):
    """
    Legacy function for backward compatibility.
    """
    tool = WebSearchTool()
    return tool.search(query) 