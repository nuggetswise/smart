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
from core.tools.time_tool import TimeTool, get_current_time
from core.agents.calendar_agent import CalendarAgent
from core.memory.long_term_memory import LongTermMemory
import json
import os
import PyPDF2
import io
from datetime import datetime, timedelta
from core.oauth_handler import get_user_credentials, is_user_authenticated, show_connect_calendar_button, show_user_info, handle_oauth_callback

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
        self.time_tool = TimeTool()
        self.memory = LongTermMemory()
        self.calendar_agent = CalendarAgent()
        
        # Load persona config
        self.persona_config = self._load_persona_config()
        
        # Start calendar agent monitoring
        self._start_calendar_agent()
        
    def _start_calendar_agent(self):
        """Start the calendar agent with notification callback."""
        def notification_callback(notification):
            """Callback for calendar notifications."""
            if 'proactive_messages' not in st.session_state:
                st.session_state.proactive_messages = []
            
            st.session_state.proactive_messages.append(notification)
        
        # Start the calendar agent
        self.calendar_agent.start_monitoring(notification_callback)
        
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
        # Handle OAuth callback first
        if handle_oauth_callback():
            return "Calendar connected successfully!"
        
        # Check if user is authenticated for calendar features
        if not is_user_authenticated() and self._is_calendar_related(message):
            return "Please connect your Google Calendar first to use calendar features."
        
        # Update calendar tool with current user credentials
        user_credentials = get_user_credentials()
        if user_credentials and self.calendar_tool.user_credentials != user_credentials:
            self.calendar_tool.update_credentials(user_credentials)
        
        # Handle file upload first
        if uploaded_file:
            return self._handle_file_upload(uploaded_file, message)
        
        # Guard against hallucination for document summary requests
        summary_triggers = [
            'summary of related documents',
            'summarize related documents',
            'summarize uploaded documents',
            'summarize uploaded files',
            'summarize the documents',
            'summarize the file',
            'summarize this file',
            'summarize this document',
            'summarize my documents',
            'summarize my files',
        ]
        if any(trigger in message.lower() for trigger in summary_triggers):
            # Check for document context (pending file or other context)
            if not st.session_state.get('pending_file'):
                return (
                    "I couldn't find any related documents to summarize. "
                    "If you have a specific file or context, please upload it or clarify your request."
                )
        
        # Check for tool-specific commands
        if message.lower().startswith('/search '):
            query = message[8:]  # Remove '/search '
            return self._handle_web_search(query)
        elif message.lower().startswith('/calendar'):
            return self._handle_calendar_check()
        elif message.lower().startswith('/summarize'):
            return "Please provide the text you'd like me to summarize."
        elif message.lower().startswith('/calendar-agent'):
            return self._handle_calendar_agent_status()
        elif message.lower().startswith('/test-notification'):
            return self._handle_test_notification()
        elif message.lower().startswith('/time'):
            return self._handle_time_query(message)
        
        # Check for time-related queries
        time_keywords = ['current time', 'what time', 'time in', 'timezone', 'what day', 'what date']
        if any(keyword in message.lower() for keyword in time_keywords):
            return self._handle_time_query(message)
        
        # --- NEW: Meeting prep/summary intent detection ---
        # If last assistant message was a meeting notification with 'Need help preparing?',
        # and user says 'yes' or similar, trigger meeting prep/summary logic.
        last_msgs = self.memory.get_all_messages()[-4:]
        last_assistant = next((m['content'] for m in reversed(last_msgs) if m['role'] == 'assistant'), None)
        if last_assistant and 'need help preparing' in last_assistant.lower():
            if message.strip().lower() in {'yes', 'yes please', 'please', 'ok', 'sure', 'y', 'yeah', 'yep'}:
                # Find the latest event from the last proactive notification
                last_event = None
                for m in reversed(last_msgs):
                    if 'Meeting Reminder' in m['content']:
                        # Try to extract event summary from the message
                        import re
                        match = re.search(r'\*\*(.*?)\*\*', m['content'])
                        event_summary = match.group(1) if match else None
                        # Try to get event from calendar agent
                        if event_summary:
                            events = self.calendar_tool.get_upcoming_events_raw(hours=24)
                            for event in events:
                                if event.get('summary') == event_summary:
                                    last_event = event
                                    break
                        break
                if last_event:
                    # Generate meeting prep/summary using the agent's AI
                    prep = self.calendar_agent._generate_meeting_insights(last_event)
                    return f"Here's your meeting preparation summary for **{last_event.get('summary')}**:\n\n{prep}"
                else:
                    return "Sorry, I couldn't find the meeting details to prepare a summary. Please specify the meeting or try again closer to the event time."
        
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
    
    def _handle_calendar_agent_status(self) -> str:
        """Handle calendar agent status check requests."""
        try:
            # Get calendar agent status
            status = self.calendar_agent.get_status()
            
            # Build response
            response = f"## 🤖 Calendar Agent Status\n\n"
            
            # Running status
            if status['running']:
                response += "✅ **Agent Status:** Running\n"
            else:
                response += "❌ **Agent Status:** Stopped\n"
            
            # Thread status
            if status['thread_alive']:
                response += "🔄 **Monitoring:** Active\n"
            else:
                response += "⏸️ **Monitoring:** Paused\n"
            
            # Configuration
            response += f"⏱️ **Check Interval:** {status['check_interval']} seconds\n"
            response += f"📊 **Notifications Sent:** {status['notified_count']}\n"
            
            if status['last_check']:
                response += f"🕐 **Last Check:** {status['last_check'][:19]}\n"
            else:
                response += "🕐 **Last Check:** Never\n"
            
            # AI capabilities
            response += f"\n🤖 **AI Capabilities:**\n"
            response += f"- AI Insights: {'✅ Enabled' if status['ai_insights_enabled'] else '❌ Disabled'}\n"
            response += f"- Meeting Prep: {'✅ Enabled' if status['meeting_prep_enabled'] else '❌ Disabled'}\n"
            
            response += "\n💡 **Commands:**"
            response += "\n- `/test-notification` - Test AI-powered notification"
            response += "\n- `/calendar` - Check upcoming events"
            
            self.memory.add_message("user", "/calendar-agent")
            self.memory.add_message("assistant", response)
            return response
            
        except Exception as e:
            error_msg = f"Calendar agent status check failed: {str(e)}"
            self.memory.add_message("user", "/calendar-agent")
            self.memory.add_message("assistant", error_msg)
            return error_msg
    
    def _handle_test_notification(self) -> str:
        """Handle test notification requests."""
        try:
            # Generate test notification
            test_notification = self.calendar_agent.test_notification()
            
            # Add to proactive messages
            if 'proactive_messages' not in st.session_state:
                st.session_state.proactive_messages = []
            
            st.session_state.proactive_messages.append(test_notification)
            
            response = "✅ **Test notification sent!** Check the chat for the AI-powered meeting reminder with insights."
            
            self.memory.add_message("user", "/test-notification")
            self.memory.add_message("assistant", response)
            return response
            
        except Exception as e:
            error_msg = f"Test notification failed: {str(e)}"
            self.memory.add_message("user", "/test-notification")
            self.memory.add_message("assistant", error_msg)
            return error_msg
    
    def _handle_conversation(self, message: str) -> str:
        """Handle regular conversation with LLM and context."""
        try:
            # Check for meeting scheduling intent first
            scheduling_keywords = ['schedule', 'book', 'set up', 'meet with', 'appointment', 'call']
            is_scheduling_request = any(keyword in message.lower() for keyword in scheduling_keywords)
            
            if is_scheduling_request:
                # Try to extract meeting details and schedule
                try:
                    # Extract attendee email
                    import re
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    emails = re.findall(email_pattern, message)
                    
                    if emails:
                        attendee_email = emails[0]
                        
                        # Extract time information
                        time_info = self._extract_time_from_message(message)
                        
                        # Create meeting title
                        meeting_title = self._generate_meeting_title(message, attendee_email)
                        
                        # Create the calendar event
                        event_result = self.calendar_tool.add_event(
                            summary=meeting_title,
                            date=time_info['date'],
                            time=time_info['time'],
                            attendees=[attendee_email],
                            location="Google Meet",
                            description=f"Meeting scheduled via SmartDesk AI"
                        )
                        
                        if event_result:
                            response = f"✅ I've scheduled a meeting with {attendee_email} for {time_info['formatted_time']}. The meeting has been added to your calendar and an invitation has been sent."
                        else:
                            response = f"❌ Failed to schedule the meeting. Please try again."
                    else:
                        response = "❌ I couldn't find an email address in your request. Please provide the attendee's email address to schedule the meeting."
                    
                    # Store in memory
                    self.memory.add_message("user", message)
                    self.memory.add_message("assistant", response)
                    return response
                    
                except Exception as e:
                    # If scheduling fails, fall back to regular conversation
                    print(f"Scheduling failed, falling back to conversation: {e}")
            
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
    
    def _extract_time_from_message(self, message: str) -> dict:
        """Extract time information from natural language message."""
        try:
            # Get current time info
            current_time_info = self.time_tool.get_time_in_toronto()
            
            # Simple time parsing - look for common patterns
            message_lower = message.lower()
            
            # Default to tomorrow at 1pm if no specific time found
            date_str = None
            time_str = None
            formatted_time = "tomorrow at 1:00 PM EST"
            
            # Look for "tomorrow" + time
            if "tomorrow" in message_lower:
                # Get tomorrow's date
                from datetime import datetime, timedelta
                tomorrow = datetime.now() + timedelta(days=1)
                date_str = tomorrow.strftime('%Y-%m-%d')
                
                if "1pm" in message_lower or "1 pm" in message_lower:
                    time_str = "13:00"
                    formatted_time = "tomorrow at 1:00 PM EST"
                elif "2pm" in message_lower or "2 pm" in message_lower:
                    time_str = "14:00"
                    formatted_time = "tomorrow at 2:00 PM EST"
                elif "3pm" in message_lower or "3 pm" in message_lower:
                    time_str = "15:00"
                    formatted_time = "tomorrow at 3:00 PM EST"
                # Add more time patterns as needed
            
            # If no specific time found, use default
            if not date_str or not time_str:
                from datetime import datetime, timedelta
                tomorrow = datetime.now() + timedelta(days=1)
                date_str = tomorrow.strftime('%Y-%m-%d')
                time_str = "13:00"
                formatted_time = "tomorrow at 1:00 PM EST"
            
            return {
                'date': date_str,
                'time': time_str,
                'formatted_time': formatted_time
            }
            
        except Exception as e:
            # Fallback to default time
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            return {
                'date': tomorrow.strftime('%Y-%m-%d'),
                'time': "13:00",
                'formatted_time': "tomorrow at 1:00 PM EST"
            }
    
    def _generate_meeting_title(self, message: str, attendee_email: str) -> str:
        """Generate a meeting title from the message and attendee."""
        # Extract name from email
        name = attendee_email.split('@')[0]
        
        # Look for meeting purpose in message
        if "discuss" in message.lower():
            return f"Discussion with {name}"
        elif "review" in message.lower():
            return f"Review with {name}"
        elif "call" in message.lower():
            return f"Call with {name}"
        else:
            return f"Meeting with {name}"
    
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
        # Get current time information
        current_time_info = self.time_tool.get_time_in_toronto()
        current_time_str = f"{current_time_info['time']} {current_time_info['timezone_abbr']} on {current_time_info['date']}"
        
        prompt = f"""You are {self.persona_config['name']}, {self.persona_config['personality']}.

You are a helpful, intelligent AI assistant that provides clear, well-structured, and actionable responses. Always aim to be:
- Direct and relevant
- Well-organized with clear sections
- Specific with concrete examples
- Professional yet friendly
- Helpful and actionable

**CURRENT TIME:** {current_time_str}

**IMPORTANT:** You have access to real-time, accurate time information. When users ask about current time, date, or timezone information, you can provide accurate, up-to-the-moment information. Do not rely on potentially outdated information from search results for time queries.

**MEETING SCHEDULING CAPABILITIES:**
When users ask to schedule meetings or appointments, you can actually create calendar events. Here's how to handle scheduling requests:

1. **Detect scheduling intent** - Look for phrases like:
   - "schedule a meeting with [person]"
   - "book an appointment"
   - "set up a call"
   - "meet with [person]"
   - "schedule [time] meeting"

2. **Extract meeting details** from the user's request:
   - Attendee email(s)
   - Date and time (support natural language like "tomorrow at 2pm EST")
   - Meeting title/summary
   - Duration (default to 30 minutes if not specified)
   - Location (default to "Google Meet" if not specified)

3. **Create the meeting** using the calendar tool:
   - Use the calendar_tool.add_event() method
   - Provide all extracted details
   - Confirm the meeting was created successfully

4. **Respond with confirmation** including:
   - Meeting details (title, time, attendees)
   - Confirmation that it was scheduled
   - Any relevant follow-up information

**Example scheduling flow:**
User: "Schedule a meeting with john@example.com tomorrow at 2pm EST"
Assistant: [Extract details and create event via calendar_tool.add_event()]
Response: "✅ I've scheduled a meeting with john@example.com for tomorrow at 2:00 PM EST. The meeting has been added to your calendar and an invitation has been sent."

**IMPORTANT:** When scheduling meetings, always use the actual calendar tool to create the event, don't just respond as if you did it.

"""
        
        # Check if user is asking about meetings or preparation
        meeting_keywords = ['meeting', 'prepare', 'preparation', 'agenda', 'attendees', 'schedule', 'calendar', 'appointment']
        is_meeting_related = any(keyword in message.lower() for keyword in meeting_keywords)
        
        # Add calendar data if meeting-related
        if is_meeting_related:
            try:
                events = self.calendar_tool.get_upcoming_events_raw(hours=24)
                if events:
                    prompt += f"""IMPORTANT: The user is asking about meetings. Here are their upcoming calendar events for the next 24 hours:

"""
                    for event in events:
                        summary = event.get('summary', 'Unknown Event')
                        start_time = event.get('start', {}).get('dateTime', 'Unknown time')
                        location = event.get('location', 'No location')
                        description = event.get('description', 'No description')
                        attendees = event.get('attendees', [])
                        
                        # Format attendees
                        attendee_list = []
                        for attendee in attendees:
                            name = attendee.get('displayName') or attendee.get('email', 'Unknown')
                            attendee_list.append(name)
                        
                        prompt += f"""📅 **{summary}**
🕐 Time: {start_time}
📍 Location: {location}
👥 Attendees: {', '.join(attendee_list) if attendee_list else 'No attendees listed'}
📝 Description: {description}

"""
                    prompt += """When the user asks about meeting preparation, use this calendar data to provide specific, actionable insights. Don't ask them for meeting details - you already have them from their calendar.

If they ask about preparing for a specific meeting, provide comprehensive preparation advice including:
- Meeting type analysis
- Key preparation points
- Suggested agenda items
- Questions to consider
- Materials needed
- Follow-up actions

Be specific and actionable based on the meeting details you have access to.

"""
                else:
                    prompt += """IMPORTANT: The user is asking about meetings, but no upcoming events were found in their calendar for the next 24 hours.

"""
            except Exception as e:
                prompt += f"""IMPORTANT: The user is asking about meetings, but there was an error accessing their calendar: {e}

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

    def _generate_meeting_prep_insights(self, event: Dict[str, Any]) -> str:
        """Generate comprehensive meeting preparation insights."""
        try:
            summary = event.get('summary', 'Unknown Meeting')
            start_time = event.get('start', {}).get('dateTime', '')
            location = event.get('location', 'No location specified')
            description = event.get('description', '')
            attendees = event.get('attendees', [])
            
            # Format attendees
            attendee_list = []
            if attendees:
                for attendee in attendees:
                    email = attendee.get('email', '')
                    name = attendee.get('displayName', email)
                    if name:  # Only add non-empty names
                        attendee_list.append(name)
            
            # Format time
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%I:%M %p")
                    formatted_date = dt.strftime("%B %d, %Y")
                except:
                    formatted_time = "TBD"
                    formatted_date = "TBD"
            else:
                formatted_time = "TBD"
                formatted_date = "TBD"
            
            # Build context for AI analysis
            context = f"""Meeting Details:
- Title: {summary}
- Time: {formatted_time} on {formatted_date}
- Location: {location}
- Description: {description}
- Attendees: {', '.join(attendee_list) if attendee_list else 'No attendees listed'}"""
            
            # AI prompt for comprehensive preparation
            prompt = f"""Based on this meeting information, provide comprehensive preparation advice:

{context}

Please provide:
1. **Meeting Type Analysis**: What type of meeting is this likely to be?
2. **Key Preparation Points**: What should be prepared in advance?
3. **Suggested Agenda Items**: What topics should be covered?
4. **Questions to Consider**: What questions should be ready?
5. **Materials Needed**: What documents or resources might be needed?
6. **Follow-up Actions**: What should be planned for after the meeting?

Format your response with clear sections and bullet points. Be specific and actionable."""

            # Get AI response
            response = self.llm_client.get_response(prompt)
            
            # Format the complete preparation guide
            prep_guide = f"""## 📋 **Meeting Preparation Guide for: {summary}**

**📅 Meeting Details:**
- **Time:** {formatted_time} on {formatted_date}
- **Location:** {location}
- **Attendees:** {', '.join(attendee_list) if attendee_list else 'No attendees listed'}

{response}

**💡 Pro Tips:**
- Review any related documents or previous meeting notes
- Prepare your key talking points in advance
- Have your questions ready
- Consider the meeting objectives and desired outcomes
- Plan for follow-up actions after the meeting

**🎯 Success Metrics:**
- Clear action items identified
- Next steps agreed upon
- All participants aligned on goals
- Follow-up meeting scheduled if needed"""
            
            return prep_guide
            
        except Exception as e:
            return f"Error generating meeting preparation insights: {e}"

    def _handle_time_query(self, message: str) -> str:
        """Handle time-related queries."""
        try:
            message_lower = message.lower()
            
            # Check for specific timezone requests
            if 'toronto' in message_lower or 'canada' in message_lower:
                time_info = self.time_tool.get_time_in_toronto()
                timezone_name = "Toronto, Canada"
            elif 'new york' in message_lower or 'nyc' in message_lower:
                time_info = self.time_tool.get_time_in_new_york()
                timezone_name = "New York, USA"
            elif 'london' in message_lower or 'uk' in message_lower:
                time_info = self.time_tool.get_time_in_london()
                timezone_name = "London, UK"
            elif 'tokyo' in message_lower or 'japan' in message_lower:
                time_info = self.time_tool.get_time_in_tokyo()
                timezone_name = "Tokyo, Japan"
            elif 'utc' in message_lower:
                time_info = self.time_tool.get_utc_time()
                timezone_name = "UTC"
            else:
                # Default to Toronto time
                time_info = self.time_tool.get_time_in_toronto()
                timezone_name = "Toronto, Canada"
            
            if 'error' in time_info:
                return f"Error getting time information: {time_info['error']}"
            
            # Format the response
            response = f"The current time in {timezone_name} is **{time_info['time']} {time_info['timezone_abbr']}** on **{time_info['date']}**."
            
            # Add to memory
            self.memory.add_message("user", message)
            self.memory.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            return f"Error handling time query: {str(e)}"

    def _is_calendar_related(self, message: str) -> bool:
        """Check if message is related to calendar functionality."""
        calendar_keywords = [
            'schedule', 'meeting', 'calendar', 'appointment', 'event',
            'book', 'set up', 'meet with', 'call', 'reminder'
        ]
        return any(keyword in message.lower() for keyword in calendar_keywords)

def route_input(message, files=None):
    # TODO: Implement intent detection and routing
    # - OCR for images
    # - Calendar agent for event queries
    # - Web search if search mode enabled
    # - Summarizer for long-form
    # - Otherwise, pass to LLM
    return {'role': 'assistant', 'content': 'This is a placeholder response from the router.'} 