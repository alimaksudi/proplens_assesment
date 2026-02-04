"""
Preference discovery node for extracting user requirements.
"""

import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.schemas import validate_preferences

logger = logging.getLogger(__name__)

PREFERENCE_EXTRACTION_PROMPT = """You are a property preference extractor. Extract property preferences from the LATEST user message.

Current known preferences (may need to be UPDATED):
{current_preferences}

Conversation:
{conversation}

IMPORTANT RULES:
1. Focus on the LATEST user message
2. If user mentions a NEW city/location, return that city - it should REPLACE the current city
3. If user says "don't care about price", "any price", "no budget limit", "whatever available" → return {{"clear_budget": true}} to REMOVE budget constraints
4. If user provides a number (e.g., "10000000", "10 million", "$5M") → set budget_max to that value in USD
5. Only include fields that are explicitly mentioned or changed

Extract preferences from the latest message. Return a JSON object:
- city: string (city name)
- country: string (2-letter code: US, AE, SG, TH, UK, etc.)
- bedrooms: integer
- bathrooms: integer
- budget_min: number (USD) - only if user specifies minimum
- budget_max: number (USD) - only if user specifies maximum/budget
- property_type: string (apartment or villa)
- completion_status: string (available or off_plan)
- features: array of strings
- clear_budget: boolean - set to true ONLY if user wants to remove budget constraints

Examples:
- "show me Chicago" → {{"city": "Chicago", "country": "US"}}
- "don't care about price" → {{"clear_budget": true}}
- "whatever is available" → {{"clear_budget": true}}
- "budget is 5 million" → {{"budget_max": 5000000}}
- "10000000" → {{"budget_max": 10000000}}

Return ONLY the JSON object, no explanation."""

PREFERENCE_RESPONSE_PROMPT = """You are a property sales assistant for Silver Land Properties.

User's current preferences:
{preferences}

Missing important information: {missing_info}

The user just said: "{user_message}"

Generate a natural response that:
1. Acknowledges what they've shared
2. Asks about ONE missing piece of information (prioritize: city > budget > bedrooms)
3. Keep it conversational and brief (2-3 sentences max)

Do not use emojis. Be professional but friendly."""


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

    llm = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0
    )

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
