"""
Preference discovery node for extracting user requirements.
"""

import json
import logging
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.schemas import validate_preferences
from agent.prompts import PREFERENCE_EXTRACTION_PROMPT, PREFERENCE_RESPONSE_PROMPT
from agent.utils.llm import get_llm

logger = logging.getLogger(__name__)


async def discover_preferences(state: ConversationState) -> ConversationState:
    """
    Extract and track user preferences from conversation.

    Asks follow-up questions to gather missing required information.
    """
    state["current_node"] = "discover_preferences"

    messages = state.get("messages", [])
    current_prefs = state.get("preferences", {})

    # Build conversation text
    conversation = "\n".join([
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in messages[-8:]
    ])

    # Use extraction LLM (temperature=0 for deterministic extraction)
    llm = get_llm(temperature=0)

    # Extract preferences
    extraction_prompt = ChatPromptTemplate.from_template(PREFERENCE_EXTRACTION_PROMPT)

    try:
        chain = extraction_prompt | llm
        response = await chain.ainvoke({
            "current_preferences": json.dumps(current_prefs),
            "conversation": conversation
        })

        # Parse extracted preferences
        extracted = {}
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            extracted = json.loads(content)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse preferences JSON: {response.content}")

        # Get user message for "no budget" detection
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break

        # Handle clear_budget flag from LLM
        if extracted.get("clear_budget"):
            current_prefs.pop("budget_min", None)
            current_prefs.pop("budget_max", None)
            extracted.pop("clear_budget", None)
            logger.info("Cleared budget constraints (LLM flag)")

        # Also check user message for "no budget" phrases as backup
        user_message_lower = user_message.lower() if user_message else ""
        no_budget_phrases = [
            "don't care about price", "dont care about price",
            "any price", "no budget", "whatever available",
            "don't care about budget", "dont care about budget",
            "doesnt matter", "doesn't matter", "no price limit",
            "price doesn't matter", "price doesnt matter",
            "any available", "whatever is available", "show me whatever",
            "just show me", "show me all", "show me everything"
        ]
        if any(phrase in user_message_lower for phrase in no_budget_phrases):
            current_prefs.pop("budget_min", None)
            current_prefs.pop("budget_max", None)
            logger.info("Cleared budget constraints based on user message")

        # Merge with existing preferences
        for key, value in extracted.items():
            if value is not None and value != "":
                current_prefs[key] = value

        # Validate and sanitize preferences
        state["preferences"] = validate_preferences(current_prefs)

        # Check if user explicitly said "no budget" - then we don't need budget
        user_cleared_budget = any(phrase in user_message_lower for phrase in no_budget_phrases)

        # Determine what's missing (only ask for budget if user didn't say "don't care")
        missing = []
        if not current_prefs.get("city"):
            missing.append("city/location")
        if not user_cleared_budget and not current_prefs.get("budget_max") and not current_prefs.get("budget_min"):
            missing.append("budget range")
        if current_prefs.get("bedrooms") is None:
            missing.append("number of bedrooms")

        # Check if preferences are complete enough
        # If user has city and either: has budget/bedrooms OR explicitly said no budget
        has_city = bool(current_prefs.get("city"))
        has_budget_or_bedrooms = (
            current_prefs.get("budget_max") is not None or
            current_prefs.get("bedrooms") is not None
        )

        state["preferences_complete"] = has_city and (has_budget_or_bedrooms or user_cleared_budget)

        # Generate response (user_message already extracted above)
        response_prompt = ChatPromptTemplate.from_template(PREFERENCE_RESPONSE_PROMPT)
        chain = response_prompt | llm

        response = await chain.ainvoke({
            "preferences": json.dumps(current_prefs),
            "missing_info": ", ".join(missing) if missing else "None - we have enough to search",
            "user_message": user_message
        })

        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })

    except Exception as e:
        logger.error(f"Error in preference discovery: {e}")
        state["messages"].append({
            "role": "assistant",
            "content": "I'd like to help you find the perfect property. Could you tell me which city you're interested in and your approximate budget?"
        })

    return state
