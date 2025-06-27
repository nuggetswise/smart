"""
Routes all chat input to the correct tool or LLM based on user intent.
"""
import streamlit as st
from typing import Dict, List, Optional, Any
from core.llm_client import LLMClient
from core.tools.ocr_tool import OCRTool
from core.tools.calendar_tool import CalendarTool
from core.tools.websearch_tool import WebSearchTool
from core.tools.summarizer import Summarizer
from core.memory.long_term_memory import LongTermMemory
import json
import os
import PyPDF2
import io

class ChatRouter:
    """
    Central router for coordinating LLM calls, tool usage, and agent responses.
    Handles user messages, file uploads, proactive agents, and memory management.
    """
    
    def __init__(self):
        """Initialize the chat router with all tools and memory."""
        self.llm_client = LLMClient()
        self.ocr_tool = OCRTool()
        self.calendar_tool = CalendarTool()
        self.websearch_tool = WebSearchTool()
        self.summarizer = Summarizer()
        self.memory = LongTermMemory()
        
        # Load persona config
        self.persona_config = self._load_persona_config()
        
    def _load_persona_config(self) -> Dict[str, Any]:
        """Load persona configuration from JSON file."""
        try:
            with open('core/memory/persona_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default persona if config not found
            return {
                "name": "SmartDesk AI",
                "personality": "Helpful, proactive, and efficient assistant",
                "memory_limit": 50,
                "proactive_agents": {
                    "calendar": True,
                    "web_search": False
                }
            }
    
    def process_user_message(self, message: str, uploaded_file: Optional[object] = None) -> str:
        """
        Process user message and optional file upload, return agent response.
        """
        # Handle file upload first
        if uploaded_file:
            return self._handle_file_upload(uploaded_file, message)
        
        # Check for tool-specific commands
        if message.lower().startswith('/search '):
            query = message[8:]  # Remove '/search '
            return self._handle_web_search(query)
        elif message.lower().startswith('/calendar'):
            return self._handle_calendar_check()
        elif message.lower().startswith('/summarize'):
            return "Please provide the text you'd like me to summarize."
        
        # Regular conversation - use LLM with context
        return self._handle_conversation(message)
    
    def _handle_file_upload(self, uploaded_file: object, message: str = "") -> str:
        """Handle file uploads (images for OCR, PDFs for text extraction)."""
        try:
            file_name = uploaded_file.name.lower()
            
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                # OCR for images
                text = self.ocr_tool.extract_text(uploaded_file)
                if text.strip():
                    response = f"✅ Image '{uploaded_file.name}' processed successfully! I can now analyze its content. What would you like to know about it?"
                    
                    if message:
                        # If user asked a question with the upload, analyze it now
                        return self._analyze_file_content(text, message, uploaded_file.name)
                else:
                    response = f"No text found in {uploaded_file.name}. Please ensure the image contains clear, readable text."
                
            elif file_name.endswith('.pdf'):
                # PDF text extraction with progress indicator
                with st.spinner(f"Processing PDF: {uploaded_file.name}..."):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    total_pages = len(pdf_reader.pages)
                    
                    for page_num in range(total_pages):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text()
                        # Update progress for large PDFs
                        if total_pages > 5:
                            st.progress((page_num + 1) / total_pages)
                
                if text.strip():
                    # Don't show raw text - just acknowledge the upload
                    response = f"✅ PDF '{uploaded_file.name}' processed successfully! I can now analyze its content. What would you like to know about it?"
                    
                    if message:
                        # If user asked a question with the upload, analyze it now
                        return self._analyze_file_content(text, message, uploaded_file.name)
                else:
                    response = f"No text found in {uploaded_file.name}. Please ensure the PDF is readable."
                
            else:
                response = f"Unsupported file type: {uploaded_file.name}"
            
            # Store in memory
            self.memory.add_message("user", f"[File upload: {uploaded_file.name}] {message}")
            self.memory.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            return f"Error processing file: {str(e)}"
    
    def _handle_web_search(self, query: str) -> str:
        """Handle web search requests."""
        try:
            results = self.websearch_tool.search(query)
            self.memory.add_message("user", f"/search {query}")
            self.memory.add_message("assistant", results)
            return results
        except Exception as e:
            return f"Web search failed: {str(e)}"
    
    def _handle_calendar_check(self) -> str:
        """Handle calendar check requests."""
        try:
            events = self.calendar_tool.get_upcoming_events()
            if events:
                response = "Upcoming calendar events:\n\n" + events
            else:
                response = "No upcoming events found."
            
            self.memory.add_message("user", "/calendar")
            self.memory.add_message("assistant", response)
            return response
        except Exception as e:
            return f"Calendar check failed: {str(e)}"
    
    def _handle_conversation(self, message: str) -> str:
        """Handle regular conversation with LLM and context."""
        try:
            # Get conversation context from memory
            context = self.memory.get_recent_messages(10)
            
            # Check if there's a pending file that should be analyzed
            pending_file_content = self._get_pending_file_content()
            
            # Get selected model from session state
            selected_model = getattr(st.session_state, 'selected_model', None)
            
            # Build prompt with context
            prompt = self._build_conversation_prompt(message, context, pending_file_content)
            
            # Get LLM response
            response = self.llm_client.get_response(prompt, selected_model)
            
            # Store in memory
            self.memory.add_message("user", message)
            self.memory.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    def _get_pending_file_content(self) -> Optional[str]:
        """Get content from pending file if it exists."""
        if hasattr(st.session_state, 'pending_file') and st.session_state.pending_file:
            try:
                file_name = st.session_state.pending_file.name.lower()
                if file_name.endswith('.pdf'):
                    # Re-read the PDF content
                    pdf_reader = PyPDF2.PdfReader(st.session_state.pending_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
                elif file_name.endswith(('.png', '.jpg', '.jpeg')):
                    # Re-extract OCR text
                    return self.ocr_tool.extract_text(st.session_state.pending_file)
            except Exception as e:
                print(f"Error reading pending file: {e}")
        return None
    
    def _build_conversation_prompt(self, message: str, context: List[Dict[str, str]], file_content: Optional[str] = None) -> str:
        """Build conversation prompt with context, persona, and file content."""
        prompt = f"""You are {self.persona_config['name']}, {self.persona_config['personality']}.

You are a helpful, intelligent AI assistant that provides clear, well-structured, and actionable responses. Always aim to be:
- Direct and relevant
- Well-organized with clear sections
- Specific with concrete examples
- Professional yet friendly
- Helpful and actionable

"""
        
        # Add file content if available
        if file_content:
            prompt += f"""IMPORTANT: The user has uploaded a file with the following content:
{file_content}

When the user asks questions about this content, provide a comprehensive analysis that:
- Directly answers their specific question
- Uses bullet points or structured format for clarity
- Highlights the most relevant details and achievements
- Is specific and quantitative when possible
- Organizes information logically (by role, company, or topic)
- Maintains a professional, helpful tone

"""
        
        if context:
            prompt += "Recent conversation context:\n"
            for msg in context:
                role = "User" if msg['role'] == 'user' else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
            prompt += "\n"
        
        prompt += f"User: {message}\nAssistant:"
        return prompt
    
    def check_proactive_agents(self) -> List[str]:
        """
        Check for proactive agent actions (calendar reminders, etc.).
        Returns list of proactive messages to display.
        """
        proactive_messages = []
        
        if self.persona_config.get("proactive_agents", {}).get("calendar", False):
            try:
                reminder = self.calendar_tool.check_for_reminders()
                if reminder:
                    proactive_messages.append(reminder)
            except Exception as e:
                # Don't show error for proactive agents, just log it
                print(f"Calendar agent error: {e}")
        
        return proactive_messages
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Get formatted chat history for UI display."""
        return self.memory.get_all_messages()
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear_memory()

    def _analyze_file_content(self, file_content: str, user_question: str, file_name: str) -> str:
        """Analyze file content based on user question."""
        try:
            # Get selected model from session state
            selected_model = getattr(st.session_state, 'selected_model', None)
            
            # Build a focused prompt for file analysis
            prompt = f"""You are {self.persona_config['name']}, {self.persona_config['personality']}.

The user has uploaded a file named '{file_name}' with the following content:
{file_content}

The user is asking: "{user_question}"

Please provide a comprehensive, well-structured analysis that directly answers their question. 

**Guidelines:**
- Focus specifically on what they're asking about
- Provide clear, actionable insights
- Use bullet points or structured format for better readability
- Highlight the most relevant details and achievements
- Be specific and quantitative when possible
- If summarizing experience, organize by role/company
- Keep the response focused and professional

**Your analysis should be:**
- Direct and relevant to the question
- Well-organized with clear sections
- Specific with concrete examples
- Professional in tone
- Helpful for understanding the person's background

Your analysis:"""
            
            response = self.llm_client.get_response(prompt, selected_model)
            
            # Store in memory
            self.memory.add_message("user", f"[File analysis request: {file_name}] {user_question}")
            self.memory.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            return f"Error analyzing file content: {str(e)}"

def route_input(message, files=None):
    # TODO: Implement intent detection and routing
    # - OCR for images
    # - Calendar agent for event queries
    # - Web search if search mode enabled
    # - Summarizer for long-form
    # - Otherwise, pass to LLM
    return {'role': 'assistant', 'content': 'This is a placeholder response from the router.'} 