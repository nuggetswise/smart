"""
Long-form summarization tool using LLM.
"""
from core.llm_client import generate_response
from core.prompts import build_summarization_prompt

class Summarizer:
    """
    Summarization tool using LLM.
    """
    def summarize(self, text: str) -> str:
        """
        Summarize long-form text using the LLM.
        """
        prompt = build_summarization_prompt(text)
        return generate_response(prompt, stream=False)

def summarize(text):
    """
    Legacy function for backward compatibility.
    """
    return Summarizer().summarize(text) 