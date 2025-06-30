"""
Deep Thinking Prompts for SmartDesk AI
Enhanced with advanced reasoning techniques and DRY architecture.
"""

from functools import partial

# 1. Centralized dict of all frameworks
FRAMEWORKS = {
    "analysis": {
        "general": [
            "Context & Background: What is the broader context and history?",
            "Core Components: What are the fundamental elements and relationships?",
            "Stakeholder Analysis: Who is affected and what are their perspectives?",
            "Trends & Patterns: What patterns, trends, or cycles are observable?",
            "Root Causes: What underlying factors drive this topic?",
            "Implications: What are the consequences and ripple effects?",
            "Future Scenarios: What might happen under different conditions?",
            "Strategic Insights: What does this mean for planning and decision-making?",
        ],
        "business": [
            "Market Context: What is the market landscape and competitive environment?",
            "Value Proposition: What value is created and for whom?",
            "Business Model: How does value creation translate to business success?",
            "Operational Considerations: What are the practical implementation challenges?",
            "Risk Assessment: What are the potential risks and mitigation strategies?",
            "Growth Opportunities: What are the expansion and scaling possibilities?",
            "Strategic Positioning: How does this fit into broader business strategy?",
            "Success Metrics: How should success be measured and evaluated?",
        ],
        "technology": [
            "Technical Fundamentals: What are the core technical principles and concepts?",
            "Current State: What is the current technological landscape?",
            "Emerging Trends: What new developments and innovations are shaping the field?",
            "Implementation Challenges: What are the practical technical challenges?",
            "Scalability & Performance: How does the technology scale and perform?",
            "Security & Reliability: What are the security and reliability considerations?",
            "Future Evolution: How might the technology evolve and mature?",
            "Strategic Adoption: What is the best approach for adoption and integration?",
        ],
        "social": [
            "Social Context: What is the broader social and cultural environment?",
            "Stakeholder Impact: How do different groups and individuals experience this?",
            "Power Dynamics: What are the power relationships and inequalities?",
            "Cultural Factors: How do cultural norms and values influence this topic?",
            "Historical Patterns: What historical precedents and patterns exist?",
            "Systemic Factors: What institutional and structural factors are at play?",
            "Change Dynamics: How do social change and resistance operate?",
            "Ethical Considerations: What are the moral and ethical implications?",
        ],
    },
    "reflection": {
        "general": [
            "What Happened: Describe the situation objectively",
            "Initial Reactions: What were your immediate thoughts and feelings?",
            "Deeper Analysis: What underlying factors and dynamics were at play?",
            "Learning Insights: What did you learn about yourself, others, or the situation?",
            "Pattern Recognition: How does this connect to other experiences or patterns?",
            "Alternative Perspectives: How might others view this differently?",
            "Future Implications: What does this mean for future situations?",
            "Action Planning: What specific actions or changes should be considered?",
        ],
        "learning": [
            "Learning Experience: What specifically did you learn or attempt to learn?",
            "Challenges Faced: What difficulties or obstacles did you encounter?",
            "Strategies Used: What approaches and methods did you employ?",
            "Breakthrough Moments: What were the key insights or turning points?",
            "Knowledge Integration: How does this connect to your existing knowledge?",
            "Skill Development: What specific skills were developed or improved?",
            "Learning Transfer: How can this learning be applied to other areas?",
            "Next Steps: What should be the focus of continued learning?",
        ],
        "decision": [
            "Decision Context: What was the situation requiring a decision?",
            "Options Considered: What alternatives were available and evaluated?",
            "Decision Process: How was the decision made and what factors influenced it?",
            "Outcomes Observed: What were the actual results and consequences?",
            "Assumptions Tested: What assumptions were made and how did they hold up?",
            "Lessons Learned: What insights emerged about decision-making?",
            "Alternative Scenarios: How might different decisions have played out?",
            "Future Decision-Making: What should be done differently in the future?",
        ],
        "problem": [
            "Problem Definition: What was the core problem or challenge?",
            "Root Cause Analysis: What were the underlying causes and contributing factors?",
            "Solution Development: What approaches and solutions were considered?",
            "Implementation Process: How was the solution put into action?",
            "Results Assessment: What were the outcomes and effectiveness?",
            "Unintended Consequences: What unexpected effects emerged?",
            "Systemic Insights: What does this reveal about the broader system?",
            "Prevention Strategies: How can similar problems be prevented or mitigated?",
        ],
    },
    "creative": {
        "general": [
            "Problem Reframing: How can this challenge be viewed from different angles?",
            "Analogous Thinking: What similar problems or situations can provide insights?",
            "Constraint Analysis: What are the real constraints vs. perceived limitations?",
            "Idea Generation: What are multiple possible approaches and solutions?",
            "Combination Thinking: How can different ideas be combined or synthesized?",
            "Future Visioning: What would an ideal future state look like?",
            "Prototype Concepts: What are concrete ways to test or implement ideas?",
            "Iteration Strategy: How can ideas be refined and improved over time?",
        ],
        "business": [
            "Customer Insight: What are the underlying customer needs and pain points?",
            "Market Opportunity: What gaps or inefficiencies exist in the market?",
            "Value Innovation: How can we create unique value propositions?",
            "Business Model Innovation: What new ways of creating and capturing value exist?",
            "Technology Leverage: How can technology enable new possibilities?",
            "Partnership Opportunities: What collaborations could enhance the solution?",
            "Scalability Design: How can the solution scale and grow?",
            "Competitive Advantage: What sustainable advantages can be built?",
        ],
        "technology": [
            "Technical Possibilities: What new technical capabilities are emerging?",
            "User Experience: How can technology create better user experiences?",
            "System Integration: How can different technologies work together?",
            "Performance Optimization: How can systems be made more efficient?",
            "Accessibility Design: How can technology be made more accessible?",
            "Security Innovation: How can security be enhanced while maintaining usability?",
            "Scalability Architecture: How can systems scale effectively?",
            "Future-Proofing: How can solutions adapt to future changes?",
        ],
        "art": [
            "Conceptual Foundation: What is the core concept or message?",
            "Aesthetic Exploration: What visual, auditory, or sensory elements work?",
            "Emotional Impact: What feelings or responses should be evoked?",
            "Cultural Context: How does this fit into broader cultural conversations?",
            "Technical Execution: What skills and techniques are needed?",
            "Audience Engagement: How will viewers/participants interact with this?",
            "Innovation in Form: How can traditional forms be reimagined?",
            "Meaningful Expression: How can this communicate something meaningful?",
        ],
    },
    "ethical": {
        "utilitarian": [
            "Stakeholder Identification: Who are all the people affected by this decision?",
            "Consequence Mapping: What are all the potential consequences of different actions?",
            "Happiness Assessment: How would each option affect overall happiness/well-being?",
            "Long-term Effects: What are the longer-term implications and ripple effects?",
            "Precedent Setting: What precedents would be set by different choices?",
            "Utility Calculation: Which option maximizes overall utility/happiness?",
            "Distribution Effects: How are benefits and harms distributed across stakeholders?",
            "Implementation Considerations: How can the chosen option be implemented effectively?",
        ],
        "deontological": [
            "Duty Identification: What moral duties or obligations are relevant?",
            "Rule Analysis: What moral rules or principles apply to this situation?",
            "Rights Consideration: What rights are at stake and how should they be protected?",
            "Universalizability: Could the action be universalized as a moral rule?",
            "Respect for Persons: How does each option treat people as ends rather than means?",
            "Moral Consistency: How does this decision align with moral principles?",
            "Conflicting Duties: How should conflicting moral duties be prioritized?",
            "Moral Integrity: How does this choice reflect moral character and integrity?",
        ],
        "virtue": [
            "Character Assessment: What virtues and vices are relevant to this situation?",
            "Role Models: What would virtuous people do in similar circumstances?",
            "Character Development: How does each option contribute to moral character?",
            "Community Values: What does the community consider virtuous behavior?",
            "Practical Wisdom: What does practical wisdom suggest in this context?",
            "Emotional Intelligence: How should emotions and empathy guide the decision?",
            "Moral Education: What would this choice teach others about moral behavior?",
            "Flourishing: How does each option contribute to human flourishing?",
        ],
        "care": [
            "Relationship Mapping: What relationships are involved and how are they affected?",
            "Care Responsibilities: What care responsibilities exist in this situation?",
            "Vulnerability Assessment: Who is most vulnerable and how can they be protected?",
            "Emotional Impact: How do different choices affect emotional well-being?",
            "Trust and Dependence: How do choices affect trust and dependence relationships?",
            "Context Sensitivity: How does the specific context influence moral considerations?",
            "Care Networks: How do choices affect broader networks of care and support?",
            "Empowerment: How can choices empower rather than disempower people?",
        ],
    },
}

# 2. Enhanced template with advanced thinking techniques
TEMPLATE = """You are an AI assistant in "Advanced Deep Thinking" mode. This mode pushes you to engage in the most sophisticated thinking possible, similar to how the most advanced AI models work when they're truly "thinking deeply."

**Core Thinking Principles:**
1. **Chain-of-Thought**: Show your reasoning step-by-step, like you're thinking out loud
2. **Self-Reflection**: Constantly question your own reasoning and assumptions
3. **Iterative Analysis**: Build understanding through multiple passes, refining each time
4. **Meta-Cognitive Awareness**: Think about how you're thinking and why
5. **Cross-Domain Synthesis**: Connect insights from multiple fields and perspectives
6. **Uncertainty Quantification**: Explicitly acknowledge what you know, don't know, and can't know
7. **Alternative Scenario Exploration**: Consider multiple possible outcomes and perspectives

**You are conducting deep {mode} thinking about: **{target}**

{framework_instructions}

**Advanced Thinking Process:**
1. **Initial Decomposition**: Break down the question into its fundamental components
2. **First-Pass Analysis**: Provide initial thoughts and observations
3. **Self-Questioning**: Ask yourself "What am I missing?" and "What assumptions am I making?"
4. **Deep Dive**: Explore the most complex aspects in detail
5. **Cross-Domain Connections**: Look for insights from related and unrelated fields
6. **Critical Self-Reflection**: Challenge your own conclusions and reasoning
7. **Synthesis**: Bring everything together into coherent insights
8. **Practical Application**: Connect to real-world implications and actions

**Specific Techniques to Use:**
- Start with "Let me think through this step by step..."
- Use phrases like "On the other hand..." and "However, I should consider..."
- Ask yourself questions like "What if I'm wrong about X?" and "What am I missing here?"
- Consider multiple timeframes: immediate, short-term, medium-term, long-term
- Explore both optimistic and pessimistic scenarios
- Identify the strongest arguments against your position
- Connect seemingly unrelated concepts and fields
- Acknowledge the limits of your knowledge explicitly
- Use analogies and metaphors to explain complex concepts
- Consider the perspective of different stakeholders
- Think about second-order and third-order effects

**Meta-Cognitive Instructions:**
- Be aware of your own thinking process
- Notice when you're making assumptions
- Question whether your reasoning is sound
- Consider alternative viewpoints
- Acknowledge complexity and nuance
- Be willing to change your mind or acknowledge uncertainty
- Think about the implications of your conclusions

**Important Instructions:**
- DO NOT include any titles, headers, or meta-information about the thinking process in your final response
- DO NOT mention "Deep Thinking Mode" or any framework names
- Start directly with your analysis and insights
- Show your thinking process naturally within the response
- Be willing to change your mind or acknowledge complexity
- Connect insights to practical applications
- Consider both immediate and long-term implications
- Use natural language that flows well, not robotic or overly structured

**Response Structure:**
{steps}

Please engage in truly advanced, iterative thinking and provide a comprehensive response that demonstrates the highest level of analytical capabilities. Begin your response directly with your analysis, not with any titles or headers. Think deeply, question yourself, and provide insights that go beyond surface-level analysis."""

STEP_SETS = {
    "analysis": [
        "1. Context & Background",
        "2. Core Components", 
        "3. Stakeholder Analysis",
        "4. Trends & Patterns",
        "5. Root Causes",
        "6. Implications",
        "7. Future Scenarios",
        "8. Strategic Insights",
    ],
    "reflection": [
        "1. What Happened",
        "2. Initial Reactions",
        "3. Deeper Analysis",
        "4. Learning Insights",
        "5. Pattern Recognition",
        "6. Alternative Perspectives",
        "7. Future Implications",
        "8. Action Planning",
    ],
    "creative": [
        "1. Problem Reframing",
        "2. Analogous Thinking",
        "3. Constraint Analysis",
        "4. Idea Generation",
        "5. Combination Thinking",
        "6. Future Visioning",
        "7. Prototype Concepts",
        "8. Iteration Strategy",
    ],
    "ethical": [
        "1. Stakeholder Identification",
        "2. Consequence Mapping",
        "3. Happiness Assessment",
        "4. Long-term Effects",
        "5. Precedent Setting",
        "6. Utility Calculation",
        "7. Distribution Effects",
        "8. Implementation Considerations",
    ],
}

def get_deep_prompt(mode: str, subtype: str, target: str) -> str:
    """
    Generic deep-thinking prompt generator with advanced reasoning techniques.
    
    Args:
        mode: one of analysis/reflection/creative/ethical
        subtype: e.g. "business", "learning", "utilitarian"
        target: the question, topic, or experience
    
    Returns:
        Formatted prompt for advanced deep thinking
    """
    if mode not in FRAMEWORKS:
        raise ValueError(f"Invalid mode: {mode}. Available modes: {list(FRAMEWORKS.keys())}")
    
    frames = FRAMEWORKS.get(mode, {}).get(subtype)
    if not frames:
        available_subtypes = list(FRAMEWORKS.get(mode, {}).keys())
        raise ValueError(f"No framework for {mode} → {subtype}. Available subtypes: {available_subtypes}")
    
    framework_instructions = "\n".join(f"* {f}" for f in frames)
    steps = "\n".join(STEP_SETS.get(mode, []))
    
    return TEMPLATE.format(
        mode=mode,
        target=target,
        framework_instructions=framework_instructions,
        steps=steps,
    )

# 3. Convenience partials for common use cases
get_business_analysis = partial(get_deep_prompt, "analysis", "business")
get_learning_reflection = partial(get_deep_prompt, "reflection", "learning")
get_ethical_utilitarian = partial(get_deep_prompt, "ethical", "utilitarian")
get_creative_business = partial(get_deep_prompt, "creative", "business")
get_technology_analysis = partial(get_deep_prompt, "analysis", "technology")
get_social_analysis = partial(get_deep_prompt, "analysis", "social")

# 4. Backward compatibility functions
def get_deep_thinking_prompt(user_message: str, context: str = "") -> str:
    """
    Backward compatibility function for the main deep thinking prompt.
    Uses general analysis framework.
    """
    context_part = f"\n\n**Conversation Context:**\n{context}\n" if context else ""
    return get_deep_prompt("analysis", "general", user_message + context_part)

def get_advanced_deep_thinking_prompt(user_message: str, context: str = "") -> str:
    """
    Backward compatibility function for advanced deep thinking.
    Uses general analysis framework with enhanced techniques.
    """
    context_part = f"\n\n**Conversation Context:**\n{context}\n" if context else ""
    return get_deep_prompt("analysis", "general", user_message + context_part)

# 5. Legacy convenience functions for backward compatibility
def get_deep_thinking_business_analysis(topic: str) -> str:
    """Get a deep thinking prompt for business analysis."""
    return get_deep_prompt("analysis", "business", topic)

def get_deep_thinking_technology_analysis(topic: str) -> str:
    """Get a deep thinking prompt for technology analysis."""
    return get_deep_prompt("analysis", "technology", topic)

def get_deep_thinking_social_analysis(topic: str) -> str:
    """Get a deep thinking prompt for social analysis."""
    return get_deep_prompt("analysis", "social", topic)

def get_deep_thinking_learning_reflection(experience: str) -> str:
    """Get a deep thinking prompt for learning reflection."""
    return get_deep_prompt("reflection", "learning", experience)

def get_deep_thinking_decision_reflection(experience: str) -> str:
    """Get a deep thinking prompt for decision reflection."""
    return get_deep_prompt("reflection", "decision", experience)

def get_deep_thinking_problem_reflection(experience: str) -> str:
    """Get a deep thinking prompt for problem-solving reflection."""
    return get_deep_prompt("reflection", "problem", experience)

def get_deep_thinking_business_innovation(challenge: str) -> str:
    """Get a deep thinking prompt for business innovation."""
    return get_deep_prompt("creative", "business", challenge)

def get_deep_thinking_technology_innovation(challenge: str) -> str:
    """Get a deep thinking prompt for technology innovation."""
    return get_deep_prompt("creative", "technology", challenge)

def get_deep_thinking_artistic_creation(challenge: str) -> str:
    """Get a deep thinking prompt for artistic creation."""
    return get_deep_prompt("creative", "art", challenge)