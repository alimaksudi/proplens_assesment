"""
Greeting node for conversation initialization.
"""

import logging
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.config import get_fallback_message
from agent.prompts import GREETING_SYSTEM_PROMPT, GREETING_USER_PROMPT
from agent.utils.llm import get_conversational_llm

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

    llm = get_conversational_llm()

    greeting_prompt = ChatPromptTemplate.from_messages([
        ("system", GREETING_SYSTEM_PROMPT),
        ("user", GREETING_USER_PROMPT)
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
            "content": get_fallback_message("greeting_error")
        })

    return state
