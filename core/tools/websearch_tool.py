"""
Web search tool using Serper.dev or DuckDuckGo, with LLM summarization.
"""
import os
from duckduckgo_search import DDGS
import requests
from core.llm_client import generate_response
from core.tools.time_tool import TimeTool, get_current_time
from core.prompts import build_web_search_prompt
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

class WebSearchTool:
    """
    Web search tool using Serper.dev or DuckDuckGo, with LLM summarization.
    """
    def __init__(self):
        self.serper_api_key = SERPER_API_KEY
        self.time_tool = TimeTool()
    
    def search(self, query: str) -> str:
        """
        Search the web and return a summarized markdown response.
        """
        # Check if this is a time-related query
        if self._is_time_query(query):
            return self._handle_time_query(query)
        
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
        prompt = build_web_search_prompt(context)
        summary = generate_response(prompt, stream=False)
        return summary
    
    def _is_time_query(self, query: str) -> bool:
        """Check if the query is asking for current time information."""
        time_keywords = [
            'current time', 'what time', 'time in', 'timezone', 'what day', 'what date',
            'current date', 'today\'s date', 'now', 'current moment', 'local time',
            'time right now', 'what is the time', 'what is the date'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in time_keywords)
    
    def _handle_time_query(self, query: str) -> str:
        """Handle time-related queries using the time tool."""
        try:
            query_lower = query.lower()
            
            # Check for specific timezone requests
            if 'toronto' in query_lower or 'canada' in query_lower:
                time_info = self.time_tool.get_time_in_toronto()
                timezone_name = "Toronto, Canada"
            elif 'new york' in query_lower or 'nyc' in query_lower:
                time_info = self.time_tool.get_time_in_new_york()
                timezone_name = "New York, USA"
            elif 'london' in query_lower or 'uk' in query_lower:
                time_info = self.time_tool.get_time_in_london()
                timezone_name = "London, UK"
            elif 'tokyo' in query_lower or 'japan' in query_lower:
                time_info = self.time_tool.get_time_in_tokyo()
                timezone_name = "Tokyo, Japan"
            elif 'utc' in query_lower:
                time_info = self.time_tool.get_utc_time()
                timezone_name = "UTC"
            else:
                # Default to Toronto time
                time_info = self.time_tool.get_time_in_toronto()
                timezone_name = "Toronto, Canada"
            
            if 'error' in time_info:
                return f"Error getting time information: {time_info['error']}"
            
            # Format the response
            response = f"""**Current Time Information**

The current time in {timezone_name} is **{time_info['time']} {time_info['timezone_abbr']}** on **{time_info['date']}**.

*This information is provided in real-time and is accurate to the current moment.*"""
            
            return response
            
        except Exception as e:
            return f"Error handling time query: {str(e)}"

def search_and_summarize(query):
    """
    Legacy function for backward compatibility.
    """
    tool = WebSearchTool()
    return tool.search(query) 