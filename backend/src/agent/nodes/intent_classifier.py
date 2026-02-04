"""
Intent classification node for understanding user messages.
"""

import logging
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.config import get_intent_categories
from agent.prompts import INTENT_CLASSIFICATION_PROMPT
from agent.utils.cache import get_cached_intent, set_intent_cache
from agent.utils.llm import get_classifier_llm

logger = logging.getLogger(__name__)


async def classify_intent(state: ConversationState) -> ConversationState:
    """
    Classify the user's intent based on their message.

    Updates state with the classified intent for routing decisions.
    """
    state["current_node"] = "classify_intent"

    messages = state.get("messages", [])
    if not messages:
        state["user_intent"] = "greeting"
        return state

    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_message = msg["content"]
            break

    if not user_message:
        state["user_intent"] = "other"
        return state

    # Check cache first
    cached_intent = get_cached_intent(user_message)
    if cached_intent:
        state["user_intent"] = cached_intent
        logger.debug(f"Using cached intent: {cached_intent}")
        return state

    # Build conversation history for context
    history = []
    for msg in messages[-6:]:  # Last 6 messages for context
        role = "User" if msg["role"] == "user" else "Assistant"
        history.append(f"{role}: {msg['content'][:200]}")

    conversation_history = "\n".join(history) if history else "No previous messages"

    llm = get_classifier_llm()

    prompt = ChatPromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)

    try:
        chain = prompt | llm
        response = await chain.ainvoke({
            "conversation_history": conversation_history,
            "user_message": user_message
        })

        intent = response.content.strip().lower()

        valid_intents = get_intent_categories()

        if intent not in valid_intents:
            intent = "other"

        state["user_intent"] = intent
        logger.debug(f"Classified intent: {intent}")

        # Cache the result
        set_intent_cache(user_message, intent)

    except Exception as e:
        logger.error(f"Error classifying intent: {e}")
        state["user_intent"] = "other"

    return state
