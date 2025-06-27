"""
Long-form summarization tool using LLM.
"""
from core.llm_client import generate_response

class Summarizer:
    """
    Summarization tool using LLM.
    """
    def summarize(self, text: str) -> str:
        """
        Summarize long-form text using the LLM.
        """
        prompt = f"Summarize the following text in a concise, actionable way for productivity:\n\n{text}\n\nSummary:"
        return generate_response(prompt, stream=False)

def summarize(text):
    """
    Legacy function for backward compatibility.
    """
    return Summarizer().summarize(text) 