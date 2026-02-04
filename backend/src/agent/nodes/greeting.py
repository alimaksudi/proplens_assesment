"""
Greeting node for conversation initialization.
"""

import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState

logger = logging.getLogger(__name__)


async def greet_user(state: ConversationState) -> ConversationState:
    """
    Greet the user and set welcoming tone.

    Only generates a greeting if this is the first message in the conversation.
    """
    state["current_node"] = "greeting"

    # If we already have assistant messages, skip greeting
    assistant_messages = [m for m in state["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        return state

    # Check if user's first message warrants a greeting response
    user_messages = [m for m in state["messages"] if m["role"] == "user"]
    if not user_messages:
        return state

    first_message = user_messages[0]["content"].lower()

    # If user starts with specific request, don't add generic greeting
    if any(word in first_message for word in ["looking for", "want", "need", "show me", "find"]):
        return state

    llm = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.7
    )

    greeting_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a professional property sales assistant for Silver Land Properties.
Your goal is to help buyers find their perfect property and book a viewing.

Generate a warm, professional greeting that:
1. Welcomes the user
2. Briefly introduces yourself as their property assistant
3. Asks how you can help them find their ideal property

Keep it under 3 sentences. Be natural and professional, not overly enthusiastic.
Do not use emojis."""),
        ("user", "The user just opened the chat with: {user_message}\n\nGenerate an appropriate greeting.")
    ])

    try:
        chain = greeting_prompt | llm
        response = await chain.ainvoke({"user_message": first_message})

        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })

    except Exception as e:
        logger.error(f"Error generating greeting: {e}")
        state["messages"].append({
            "role": "assistant",
            "content": "Welcome to Silver Land Properties. I'm here to help you find your ideal property. What are you looking for today?"
        })

    return state
