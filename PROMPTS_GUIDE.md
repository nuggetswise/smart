# SmartDesk AI Prompts Guide

This document provides a comprehensive overview of all AI prompts used throughout the SmartDesk AI application. All prompts are centralized in `core/prompts.py` for consistency and easy management.

## 📁 File Structure

```
core/
├── prompts.py          # Centralized prompts file
├── chat_router.py      # Uses prompts for conversation handling
├── agents/
│   └── calendar_agent.py  # Uses prompts for meeting insights
└── tools/
    ├── websearch_tool.py  # Uses prompts for search summaries
    └── summarizer.py      # Uses prompts for text summarization
```

## 🎯 Core Prompt Categories

### 1. System and Persona Prompts

#### `get_system_prompt(persona_name, persona_personality, current_time)`
- **Purpose**: Main system prompt that defines the AI's role and capabilities
- **Usage**: Used in all conversation interactions
- **Key Features**:
  - Defines AI personality and behavior guidelines
  - Includes current time information
  - Emphasizes real-time time capabilities

#### `get_meeting_scheduling_prompt()`
- **Purpose**: Instructions for handling meeting scheduling requests
- **Usage**: Included in conversation prompts when scheduling is needed
- **Key Features**:
  - Detects scheduling intent
  - Extracts meeting details
  - Provides step-by-step scheduling process

### 2. Calendar and Meeting Prompts

#### `get_calendar_context_prompt(events)`
- **Purpose**: Provides calendar context when users ask about meetings
- **Usage**: Automatically included when meeting-related keywords are detected
- **Key Features**:
  - Lists upcoming events for next 5 business days
  - Formats event details (time, location, attendees, description)
  - Provides preparation guidance

#### `get_meeting_prep_prompt(meeting_context)`
- **Purpose**: Generates comprehensive meeting preparation advice
- **Usage**: When users ask for meeting preparation help
- **Key Features**:
  - Meeting type analysis
  - Key preparation points
  - Suggested agenda items
  - Questions to consider
  - Materials needed
  - Follow-up actions

#### `get_meeting_insights_prompt(meeting_context)`
- **Purpose**: Generates brief, actionable meeting insights
- **Usage**: Used by calendar agent for proactive notifications
- **Key Features**:
  - Meeting type and purpose analysis
  - Key preparation points
  - Potential talking points or questions

### 3. File Analysis Prompts

#### `get_file_analysis_prompt(file_content, user_question, file_name, persona_name, persona_personality)`
- **Purpose**: Analyzes uploaded file content based on user questions
- **Usage**: When users upload files and ask specific questions
- **Key Features**:
  - Focuses on user's specific question
  - Provides structured analysis
  - Highlights relevant details and achievements
  - Maintains professional tone

### 4. Web Search and Summarization Prompts

#### `get_web_search_summary_prompt(web_results)`
- **Purpose**: Summarizes web search results
- **Usage**: After performing web searches
- **Key Features**:
  - Includes hyperlinks in markdown
  - Provides concise summaries
  - Maintains research assistant persona

#### `get_summarization_prompt(text)`
- **Purpose**: General text summarization for productivity
- **Usage**: For long-form content summarization
- **Key Features**:
  - Concise, actionable summaries
  - Productivity-focused approach

### 5. Conversation Context Prompts

#### `get_conversation_context_prompt(context)`
- **Purpose**: Adds recent conversation history to prompts
- **Usage**: Maintains conversation continuity
- **Key Features**:
  - Formats user/assistant messages
  - Preserves conversation flow

#### `get_user_message_prompt(message)`
- **Purpose**: Formats the current user message
- **Usage**: Standard format for user input

### 6. Error and Fallback Prompts

#### `get_calendar_error_prompt(error)`
- **Purpose**: Handles calendar access errors gracefully
- **Usage**: When calendar operations fail

#### `get_generic_error_prompt(error)`
- **Purpose**: Handles general errors with helpful guidance
- **Usage**: For unexpected errors

### 7. Notification and Reminder Prompts

#### `get_meeting_reminder_template()`
- **Purpose**: Template for meeting reminder notifications
- **Usage**: Calendar agent proactive notifications
- **Key Features**:
  - Meeting details formatting
  - AI insights integration
  - Helpful follow-up suggestions

#### `get_test_notification_content()`
- **Purpose**: Content for testing notification system
- **Usage**: Calendar agent testing

### 8. Time and Utility Prompts

#### `get_time_response_template(timezone_name, time_info)`
- **Purpose**: Standardized time response format
- **Usage**: Time-related queries
- **Key Features**:
  - Real-time accuracy emphasis
  - Professional formatting

## 🔧 Prompt Builders

### `build_conversation_prompt()`
- **Purpose**: Builds complete conversation prompts with all components
- **Parameters**:
  - `message`: Current user message
  - `context`: Conversation history
  - `file_content`: Uploaded file content (optional)
  - `persona_name`: AI persona name
  - `persona_personality`: AI personality description
  - `current_time`: Current time information
  - `calendar_events`: Upcoming calendar events (optional)

### `build_file_analysis_prompt()`
- **Purpose**: Builds file analysis prompts
- **Parameters**: File content, user question, file name, persona details

### `build_meeting_prep_prompt()`
- **Purpose**: Builds meeting preparation prompts
- **Parameters**: Meeting context

### `build_meeting_insights_prompt()`
- **Purpose**: Builds meeting insights prompts
- **Parameters**: Meeting context

### `build_web_search_prompt()`
- **Purpose**: Builds web search summary prompts
- **Parameters**: Web search results

### `build_summarization_prompt()`
- **Purpose**: Builds text summarization prompts
- **Parameters**: Text to summarize

## 📝 Usage Examples

### Basic Conversation
```python
from core.prompts import build_conversation_prompt

prompt = build_conversation_prompt(
    message="What meetings do I have today?",
    context=conversation_history,
    persona_name="SmartDesk AI",
    persona_personality="a helpful, intelligent AI assistant",
    current_time="2:30 PM EST on June 30, 2025",
    calendar_events=upcoming_events
)
```

### File Analysis
```python
from core.prompts import build_file_analysis_prompt

prompt = build_file_analysis_prompt(
    file_content="Resume content...",
    user_question="What are my key achievements?",
    file_name="resume.pdf",
    persona_name="SmartDesk AI",
    persona_personality="a helpful, intelligent AI assistant"
)
```

### Meeting Preparation
```python
from core.prompts import build_meeting_prep_prompt

prompt = build_meeting_prep_prompt(
    meeting_context="Meeting: Team Standup\nTime: 9:00 AM\nAttendees: John, Jane, Bob"
)
```

## 🎨 Customization

### Modifying Prompts
1. Edit the appropriate function in `core/prompts.py`
2. Test the changes with different scenarios
3. Update this documentation if needed

### Adding New Prompts
1. Add the new prompt function to `core/prompts.py`
2. Create a corresponding builder function if needed
3. Update the imports in relevant files
4. Add documentation here

### Environment Variables
Some prompts can be customized via environment variables:
- `SYSTEM_PROMPT`: Override default system prompt (in utils/llm.py)

## 🔍 Best Practices

1. **Consistency**: Use the centralized prompts for all AI interactions
2. **Clarity**: Keep prompts clear and specific
3. **Context**: Include relevant context when building prompts
4. **Testing**: Test prompts with various scenarios
5. **Documentation**: Update this guide when modifying prompts

## 🚀 Future Enhancements

- [ ] Add prompt versioning
- [ ] Implement prompt A/B testing
- [ ] Add prompt performance metrics
- [ ] Create prompt templates for different use cases
- [ ] Add multilingual prompt support

## 📚 Related Files

- `core/prompts.py`: Main prompts file
- `core/chat_router.py`: Uses prompts for conversation handling
- `core/agents/calendar_agent.py`: Uses prompts for meeting insights
- `core/tools/websearch_tool.py`: Uses prompts for search summaries
- `core/tools/summarizer.py`: Uses prompts for text summarization
- `utils/llm.py`: Legacy utility with separate prompt handling 