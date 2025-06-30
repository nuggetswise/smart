"""
Web search tool using Serper.dev or DuckDuckGo, with LLM summarization and enhanced analysis types.
"""
import os
from duckduckgo_search import DDGS
import requests
from core.llm_client import generate_response
from core.tools.time_tool import TimeTool, get_current_time
from core.prompts import build_web_search_prompt
from dotenv import load_dotenv
import re

load_dotenv()
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

class WebSearchTool:
    """
    Web search tool using Serper.dev or DuckDuckGo, with LLM summarization and enhanced analysis types.
    """
    def __init__(self):
        self.serper_api_key = SERPER_API_KEY
        self.time_tool = TimeTool()
    
    def search(self, query: str, analysis_type: str = "auto", user_context: str = "") -> str:
        """
        Search the web and return a structured analysis based on the query type.
        
        Args:
            query: Search query
            analysis_type: Type of analysis ("auto", "summary", "analysis", "comparison", "learning")
            user_context: Additional context about the user's needs
        """
        # Check if this is a time-related query
        if self._is_time_query(query):
            return self._handle_time_query(query)
        
        # Auto-detect analysis type if not specified
        if analysis_type == "auto":
            analysis_type = self._detect_analysis_type(query)
        
        # Get search results
        results = self._get_search_results(query)
        
        if not results:
            return "No search results found. Please try a different query or check your internet connection."
        
        # Build context for LLM
        context = self._build_search_context(results)
        
        # Build appropriate prompt based on analysis type
        if analysis_type == "comparison":
            comparison_criteria = self._extract_comparison_criteria(query)
            prompt = build_web_search_prompt(context, "comparison", user_context, comparison_criteria)
            # Use deep thinking mode for complex comparisons
            summary = generate_response(prompt, stream=False, mode="deep_thinking")
        elif analysis_type == "learning":
            learning_objective = self._extract_learning_objective(query)
            prompt = build_web_search_prompt(context, "learning", user_context, "", learning_objective)
            # Use deep thinking mode for learning guides
            summary = generate_response(prompt, stream=False, mode="deep_thinking")
        elif analysis_type == "analysis":
            prompt = build_web_search_prompt(context, "analysis", user_context)
            # Use deep thinking mode for detailed analysis
            summary = generate_response(prompt, stream=False, mode="deep_thinking")
        else:
            # Default to summary - use chat mode for simple summaries
            prompt = build_web_search_prompt(context, "summary")
            summary = generate_response(prompt, stream=False, mode="chat")
        
        return summary
    
    def _get_search_results(self, query: str) -> list:
        """Get search results from available providers."""
        results = []
        
        # Try Serper.dev first (if API key available)
        if self.serper_api_key:
            try:
                resp = requests.post(
                    'https://google.serper.dev/search', 
                    json={'q': query, 'num': 10}, 
                    headers={'X-API-KEY': self.serper_api_key}
                )
                if resp.ok:
                    data = resp.json()
                    results = data.get('organic', [])
                    # Also include knowledge graph if available
                    if 'knowledgeGraph' in data:
                        results.insert(0, {
                            'title': data['knowledgeGraph'].get('title', ''),
                            'snippet': data['knowledgeGraph'].get('description', ''),
                            'link': data['knowledgeGraph'].get('link', '')
                        })
            except Exception as e:
                print(f"Serper.dev search failed: {e}")
        
        # Fallback to DuckDuckGo if no results or Serper failed
        if not results:
            try:
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=10):
                        if 'href' in r and 'body' in r:
                            results.append({
                                'title': r.get('title', ''),
                                'snippet': r['body'],
                                'link': r['href']
                            })
                        if len(results) >= 10:
                            break
            except Exception as e:
                print(f"DuckDuckGo search failed: {e}")
        
        return results
    
    def _build_search_context(self, results: list) -> str:
        """Build formatted context from search results."""
        if not results:
            return "No search results found."
        
        context_parts = []
        for i, result in enumerate(results[:8], 1):  # Limit to top 8 results
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description')
            link = result.get('link', 'No link')
            
            context_parts.append(f"**Source {i}: {title}**\n{snippet}\nLink: {link}\n")
        
        return '\n'.join(context_parts)
    
    def _detect_analysis_type(self, query: str) -> str:
        """Auto-detect the type of analysis needed based on query keywords."""
        query_lower = query.lower()
        
        # Comparison keywords
        comparison_keywords = [
            'vs', 'versus', 'compare', 'comparison', 'difference between', 'which is better',
            'pros and cons', 'advantages disadvantages', 'alternatives', 'options',
            'best', 'top', 'ranking', 'review', 'reviews'
        ]
        
        # Learning keywords
        learning_keywords = [
            'how to', 'learn', 'tutorial', 'guide', 'steps', 'process', 'method',
            'training', 'course', 'education', 'skill', 'technique', 'strategy',
            'what is', 'definition', 'explain', 'understand', 'basics', 'fundamentals'
        ]
        
        # Analysis keywords
        analysis_keywords = [
            'analysis', 'trend', 'market', 'industry', 'research', 'study',
            'report', 'statistics', 'data', 'forecast', 'prediction', 'future',
            'impact', 'effect', 'consequence', 'strategy', 'planning'
        ]
        
        # Check for comparison intent
        if any(keyword in query_lower for keyword in comparison_keywords):
            return "comparison"
        
        # Check for learning intent
        if any(keyword in query_lower for keyword in learning_keywords):
            return "learning"
        
        # Check for analysis intent
        if any(keyword in query_lower for keyword in analysis_keywords):
            return "analysis"
        
        # Default to summary
        return "summary"
    
    def _extract_comparison_criteria(self, query: str) -> str:
        """Extract comparison criteria from the query."""
        query_lower = query.lower()
        
        # Common comparison criteria
        criteria_keywords = {
            'cost': ['price', 'cost', 'expensive', 'cheap', 'budget', 'affordable'],
            'quality': ['quality', 'performance', 'efficiency', 'effectiveness'],
            'time': ['speed', 'fast', 'slow', 'duration', 'time'],
            'features': ['features', 'functionality', 'capabilities', 'tools'],
            'reliability': ['reliable', 'stable', 'dependable', 'trustworthy'],
            'support': ['support', 'customer service', 'help', 'documentation']
        }
        
        found_criteria = []
        for criterion, keywords in criteria_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                found_criteria.append(criterion)
        
        if found_criteria:
            return f"Focus on: {', '.join(found_criteria)}"
        else:
            return "Compare across: cost, quality, features, and user experience"
    
    def _extract_learning_objective(self, query: str) -> str:
        """Extract learning objective from the query."""
        # Look for specific learning goals
        learning_patterns = [
            r'learn (?:how to )?([^.]+)',
            r'understand ([^.]+)',
            r'guide (?:to|for) ([^.]+)',
            r'tutorial (?:on|for) ([^.]+)',
            r'steps (?:to|for) ([^.]+)'
        ]
        
        for pattern in learning_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no specific pattern found, use the query itself
        return query
    
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
                time_info = self.time_tool.get_current_time('toronto')
                timezone_name = "Toronto, Canada"
            elif 'new york' in query_lower or 'nyc' in query_lower:
                time_info = self.time_tool.get_current_time('new_york')
                timezone_name = "New York, USA"
            elif 'london' in query_lower or 'uk' in query_lower:
                time_info = self.time_tool.get_current_time('london')
                timezone_name = "London, UK"
            elif 'tokyo' in query_lower or 'japan' in query_lower:
                time_info = self.time_tool.get_current_time('tokyo')
                timezone_name = "Tokyo, Japan"
            elif 'utc' in query_lower:
                time_info = self.time_tool.get_current_time('utc')
                timezone_name = "UTC"
            else:
                # Default to Toronto time
                time_info = self.time_tool.get_current_time('toronto')
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

def search_and_summarize(query, analysis_type="auto", user_context=""):
    """
    Enhanced legacy function for backward compatibility.
    """
    tool = WebSearchTool()
    return tool.search(query, analysis_type, user_context) 