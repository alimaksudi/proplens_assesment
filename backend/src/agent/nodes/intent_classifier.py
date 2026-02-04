"""
Intent classification node for understanding user messages.
"""

import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState

logger = logging.getLogger(__name__)

INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a property sales chatbot.

Analyze the user's message and classify their intent into one of these categories:
- greeting: User is saying hello or starting conversation
- share_preferences: User is sharing/updating property preferences including:
  * Location/city mentions (e.g., "in Dubai", "Chicago", "suggest places in X")
  * Budget mentions (e.g., "under $500k", "budget of 1 million")
  * Bedroom/size preferences (e.g., "2-bedroom", "3 beds")
  * Property type (e.g., "apartment", "villa")
  * ANY change to search criteria or new location request
- ask_question: User is asking a question about a property or general inquiry (not changing search criteria)
- request_recommendations: User wants to see results with CURRENT criteria (e.g., "show me", "what do you have")
- express_interest: User is showing interest in a SPECIFIC property already shown
- book_viewing: User wants to schedule a property viewing. This includes:
  * Direct requests: "schedule a viewing", "book a visit", "I want to see it"
  * Affirmative responses when viewing was offered: "yes", "yes please", "sure", "I'd like that", "let's do it", "okay"
- provide_contact: User is providing contact information (name, email, phone)
- clarify: User is clarifying or correcting previous information
- goodbye: User is ending the conversation (e.g., "bye", "goodbye", "thanks bye", "see you", "take care", "gotta go", "that's all", "thanks", "thank you")
- other: None of the above

IMPORTANT RULES:
1. If user mentions a NEW city/location, classify as share_preferences
2. If the assistant just offered to schedule a viewing and user says "yes", "sure", "please", "okay" - classify as book_viewing
3. Short affirmative responses ("yes", "yes please", "sure") after a viewing offer = book_viewing

Conversation context:
{conversation_history}

Current user message: {user_message}

Respond with ONLY the intent category (one word from the list above)."""


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

    # Build conversation history for context
    history = []
    for msg in messages[-6:]:  # Last 6 messages for context
        role = "User" if msg["role"] == "user" else "Assistant"
        history.append(f"{role}: {msg['content'][:200]}")

    conversation_history = "\n".join(history) if history else "No previous messages"

    llm = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)

    try:
        chain = prompt | llm
        response = await chain.ainvoke({
            "conversation_history": conversation_history,
            "user_message": user_message
        })

        intent = response.content.strip().lower()

        valid_intents = [
            "greeting", "share_preferences", "ask_question",
            "request_recommendations", "express_interest", "book_viewing",
            "provide_contact", "clarify", "goodbye", "other"
        ]

        if intent not in valid_intents:
            intent = "other"

        state["user_intent"] = intent
        logger.debug(f"Classified intent: {intent}")

    except Exception as e:
        logger.error(f"Error classifying intent: {e}")
        state["user_intent"] = "other"

    return state
