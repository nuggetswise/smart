"""
Centralized prompts for SmartDesk AI
All AI prompts used throughout the application are defined here for consistency and easy management.
"""

# =============================================================================
# CORE PERSONA AND SYSTEM PROMPTS
# =============================================================================

def get_system_prompt(persona_name: str, persona_personality: str, current_time: str) -> str:
    """Get the main system prompt for the AI assistant."""
    return f"""You are {persona_name}, {persona_personality}.

You are a helpful, intelligent AI assistant that provides clear, well-structured, and actionable responses. Always aim to be:
- Direct and relevant
- Well-organized with clear sections
- Specific with concrete examples
- Professional yet friendly
- Helpful and actionable

**CURRENT TIME:** {current_time}

**IMPORTANT:** You have access to real-time, accurate time information. When users ask about current time, date, or timezone information, you can provide accurate, up-to-the-moment information. Do not rely on potentially outdated information from search results for time queries."""

def get_meeting_scheduling_prompt() -> str:
    """Get the meeting scheduling capabilities prompt."""
    return """**MEETING SCHEDULING CAPABILITIES:**
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

**IMPORTANT:** When scheduling meetings, always use the actual calendar tool to create the event, don't just respond as if you did it."""

def get_calendar_context_prompt(events: list) -> str:
    """Get prompt for when user is asking about meetings with calendar context."""
    if not events:
        return """IMPORTANT: The user is asking about meetings, but no upcoming events were found in their calendar for the next 24 hours."""
    
    prompt = f"""IMPORTANT: The user is asking about meetings. Here are their upcoming calendar events for the next 24 hours:

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

Be specific and actionable based on the meeting details you have access to."""
    
    return prompt

def get_file_analysis_prompt(file_content: str, user_question: str, file_name: str, persona_name: str, persona_personality: str) -> str:
    """Get prompt for file content analysis."""
    return f"""You are {persona_name}, {persona_personality}.

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

# =============================================================================
# MEETING PREPARATION AND INSIGHTS PROMPTS
# =============================================================================

def get_meeting_prep_prompt(meeting_context: str) -> str:
    """Get prompt for comprehensive meeting preparation advice."""
    return f"""Based on this meeting information, provide comprehensive preparation advice:

{meeting_context}

Please provide:
1. **Meeting Type Analysis**: What type of meeting is this likely to be?
2. **Key Preparation Points**: What should be prepared in advance?
3. **Suggested Agenda Items**: What topics should be covered?
4. **Questions to Consider**: What questions should be ready?
5. **Materials Needed**: What documents or resources might be needed?
6. **Follow-up Actions**: What should be planned for after the meeting?

Format your response with clear sections and bullet points. Be specific and actionable."""

def get_meeting_insights_prompt(meeting_context: str) -> str:
    """Get prompt for generating meeting insights."""
    return f"""Analyze this meeting and provide 2-3 brief, actionable insights:

{meeting_context}

Provide insights about:
1. Meeting type and purpose
2. Key preparation points
3. Potential talking points or questions

Keep each insight to 1-2 sentences. Be specific and actionable."""

# =============================================================================
# WEB SEARCH AND SUMMARIZATION PROMPTS
# =============================================================================

def get_web_search_summary_prompt(web_results: str) -> str:
    """Get prompt for summarizing web search results."""
    return f"""You are a research assistant. Summarize the following web results for the user. Include hyperlinks in markdown.

Web results:
{web_results}

Summary:"""

def get_summarization_prompt(text: str) -> str:
    """Get prompt for general text summarization."""
    return f"""Summarize the following text in a concise, actionable way for productivity:

{text}

Summary:"""

# =============================================================================
# CONVERSATION CONTEXT PROMPTS
# =============================================================================

def get_conversation_context_prompt(context: list) -> str:
    """Get prompt for adding conversation context."""
    if not context:
        return ""
    
    prompt = "Recent conversation context:\n"
    for msg in context:
        role = "User" if msg['role'] == 'user' else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "\n"
    
    return prompt

def get_user_message_prompt(message: str) -> str:
    """Get prompt for user message."""
    return f"User: {message}\nAssistant:"

# =============================================================================
# ERROR AND FALLBACK PROMPTS
# =============================================================================

def get_calendar_error_prompt(error: str) -> str:
    """Get prompt for calendar access errors."""
    return f"""IMPORTANT: The user is asking about meetings, but there was an error accessing their calendar: {error}"""

def get_generic_error_prompt(error: str) -> str:
    """Get prompt for generic errors."""
    return f"""I encountered an error while processing your request: {error}

Please try again or rephrase your question. If the problem persists, you may need to reconnect your calendar or check your settings."""

# =============================================================================
# NOTIFICATION AND REMINDER PROMPTS
# =============================================================================

def get_meeting_reminder_template() -> str:
    """Get template for meeting reminder notifications."""
    return """🔔 **Meeting Reminder**

📅 **{summary}**
🕐 **Time:** {formatted_time} on {formatted_date}
📍 **Location:** {location}
👥 **Attendees:** {attendees}

📝 **Description:** {description}

🤖 **AI Insights:**
{ai_insights}

💡 **Need help preparing?** Ask me about the meeting or request a summary of related documents!"""

def get_test_notification_content() -> str:
    """Get content for test notifications."""
    return """🔔 **Test Meeting with AI Insights**

📅 **Test Meeting with AI Insights**
🕐 **Time:** Starting in 10 minutes
📍 **Location:** Test Conference Room
👥 **Attendees:** Test User, AI Assistant

📝 **Description:** This is a test meeting to demonstrate AI-powered calendar agent capabilities

🤖 **AI Insights:**
- This appears to be a demonstration meeting to showcase AI capabilities
- Key preparation: Review the AI features being tested
- Consider: How to apply these insights to real meetings

💡 **Need help preparing?** Ask me about the meeting or request a summary of related documents!"""

# =============================================================================
# TIME AND UTILITY PROMPTS
# =============================================================================

def get_time_response_template(timezone_name: str, time_info: dict) -> str:
    """Get template for time responses."""
    return f"""**Current Time Information**

The current time in {timezone_name} is **{time_info['time']} {time_info['timezone_abbr']}** on **{time_info['date']}**.

*This information is provided in real-time and is accurate to the current moment.*"""

# =============================================================================
# PROMPT BUILDERS
# =============================================================================

def build_conversation_prompt(
    message: str, 
    context: list, 
    file_content: str = None, 
    persona_name: str = "SmartDesk AI",
    persona_personality: str = "a helpful, intelligent AI assistant",
    current_time: str = None,
    calendar_events: list = None
) -> str:
    """Build a complete conversation prompt with all necessary components."""
    
    # Start with system prompt
    prompt = get_system_prompt(persona_name, persona_personality, current_time or "Current time not available")
    
    # Add meeting scheduling capabilities
    prompt += "\n\n" + get_meeting_scheduling_prompt()
    
    # Add calendar context if meeting-related
    if calendar_events is not None:
        prompt += "\n\n" + get_calendar_context_prompt(calendar_events)
    
    # Add file content if available
    if file_content:
        prompt += f"\n\nIMPORTANT: The user has uploaded a file with the following content:\n{file_content}\n\n"
        prompt += """When the user asks questions about this content, provide a comprehensive analysis that:
- Directly answers their specific question
- Uses bullet points or structured format for clarity
- Highlights the most relevant details and achievements
- Is specific and quantitative when possible
- Organizes information logically (by role, company, or topic)
- Maintains a professional, helpful tone"""
    
    # Add conversation context
    prompt += "\n\n" + get_conversation_context_prompt(context)
    
    # Add user message
    prompt += get_user_message_prompt(message)
    
    return prompt

def build_file_analysis_prompt(
    file_content: str, 
    user_question: str, 
    file_name: str,
    persona_name: str = "SmartDesk AI",
    persona_personality: str = "a helpful, intelligent AI assistant"
) -> str:
    """Build a file analysis prompt."""
    return get_file_analysis_prompt(file_content, user_question, file_name, persona_name, persona_personality)

def build_meeting_prep_prompt(meeting_context: str) -> str:
    """Build a meeting preparation prompt."""
    return get_meeting_prep_prompt(meeting_context)

def build_meeting_insights_prompt(meeting_context: str) -> str:
    """Build a meeting insights prompt."""
    return get_meeting_insights_prompt(meeting_context)

def build_web_search_prompt(web_results: str) -> str:
    """Build a web search summary prompt."""
    return get_web_search_summary_prompt(web_results)

def build_summarization_prompt(text: str) -> str:
    """Build a summarization prompt."""
    return get_summarization_prompt(text) 