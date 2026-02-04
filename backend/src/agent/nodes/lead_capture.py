"""
Lead capture node for collecting user contact information.
"""

import os
import json
import re
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.schemas import validate_lead_data
from agent.tools import get_booking_tool
from domain.models import Lead

logger = logging.getLogger(__name__)

LEAD_EXTRACTION_PROMPT = """Extract contact information from the user's message.

Current known information:
{current_lead}

User's message: {message}

Extract any NEW information found. Return a JSON object with only fields that have values:
- first_name: string
- last_name: string
- email: string (must be valid email format)
- phone: string

Return ONLY the JSON object, no explanation. Return {{}} if no new info found."""

LEAD_FOLLOWUP_PROMPT = """You are a property sales assistant for Silver Land Properties.

We're collecting information for a viewing booking.

Information collected so far:
{lead_info}

Still needed: {missing_info}

User just said: "{user_message}"

Generate a brief response that:
1. Thanks them for the information they provided (if any)
2. Asks for the NEXT missing piece of information (prioritize: name > email > phone)
   - Ask for "name" (user's full name), not "first name" separately
   - If name is provided, ask for email

Keep it to 1-2 sentences. Be professional. Do not use emojis."""


def extract_email(text: str) -> str:
    """Extract email address from text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract phone number from text."""
    phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else ""


async def capture_lead_details(state: ConversationState) -> ConversationState:
    """
    Capture lead contact information progressively.

    Extracts information from user messages and asks for missing details.
    """
    state["current_node"] = "capture_lead"

    messages = state.get("messages", [])
    # IMPORTANT: Make a copy of lead_data to avoid reference issues
    lead_data = dict(state.get("lead_data", {}))

    # Get user message
    user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_message = msg["content"]
            break

    # ALWAYS try direct extraction first (before LLM) - this is more reliable
    extracted = {}

    # Direct email extraction - check user message for email
    if not lead_data.get("email"):
        email = extract_email(user_message)
        if email:
            extracted["email"] = email
            logger.info(f"Directly extracted email: {email}")

    # Direct phone extraction
    if not lead_data.get("phone"):
        phone = extract_phone(user_message)
        if phone:
            extracted["phone"] = phone

    # Parse full name from message - handles:
    # - "Ali" → first_name: "Ali", last_name: ""
    # - "Ali Maksudi" → first_name: "Ali", last_name: "Maksudi"
    # - "Ali Bin Maksudi" → first_name: "Ali", last_name: "Bin Maksudi"
    if not lead_data.get("first_name"):
        words = user_message.strip().split()

        # Don't extract as name if it looks like a property name from search results
        search_results = state.get("search_results", [])
        is_property_mention = False
        for prop in search_results:
            prop_name_lower = prop.get("project_name", "").lower()
            if any(word.lower() in prop_name_lower for word in words):
                is_property_mention = True
                break

        # Don't extract as name if it looks like an email
        is_email = "@" in user_message

        # Allow up to 5 words for full name (e.g., "Muhammad Ali Bin Abdul Rahman")
        if not is_property_mention and not is_email and len(words) <= 5 and words:
            first_word = words[0]
            # Check if first word looks like a name (alphabetic, may include apostrophe/hyphen)
            if first_word.replace("'", "").replace("-", "").isalpha():
                extracted["first_name"] = first_word.title()

                # Everything after first word becomes last_name
                if len(words) >= 2:
                    last_name_parts = words[1:]
                    # Validate all parts are name-like
                    if all(w.replace("'", "").replace("-", "").isalpha() for w in last_name_parts):
                        extracted["last_name"] = " ".join(w.title() for w in last_name_parts)

    # Try LLM extraction for additional info (but don't rely on it solely)
    llm = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0
    )

    extraction_prompt = ChatPromptTemplate.from_template(LEAD_EXTRACTION_PROMPT)

    try:
        chain = extraction_prompt | llm
        response = await chain.ainvoke({
            "current_lead": json.dumps(lead_data),
            "message": user_message
        })

        # Parse LLM extracted info
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            llm_extracted = json.loads(content)

            # Merge LLM results (but direct extraction takes priority)
            for key, value in llm_extracted.items():
                if value and not extracted.get(key):
                    extracted[key] = value
        except json.JSONDecodeError:
            pass

    except Exception as e:
        logger.warning(f"LLM extraction failed (using direct extraction): {e}")

    # Merge extracted data with existing lead_data
    for key, value in extracted.items():
        if value:
            lead_data[key] = value

    # Validate and sanitize lead data
    validated_lead_data = validate_lead_data(lead_data)
    state["lead_data"] = validated_lead_data

    logger.info(f"Lead data after extraction: {validated_lead_data}")

    # Ensure selected_project_id is set if we have search results
    # This handles the case where user goes directly to capture_lead via provide_contact intent
    search_results = state.get("search_results", [])
    logger.info(f"capture_lead - selected_project_id: {state.get('selected_project_id')}, search_results count: {len(search_results)}")
    if search_results:
        logger.info(f"First search result: {search_results[0].get('project_name', 'NO NAME')} (id={search_results[0].get('id', 'NO ID')})")

    if not state.get("selected_project_id") and search_results:
        # Default to first result
        state["selected_project_id"] = search_results[0]["id"]
        logger.info(f"Set selected_project_id to first result: {search_results[0]['id']}")

        # Try to match property name from recent messages
        recent_user_text = " ".join([
            msg["content"].lower()
            for msg in messages[-6:]
            if msg.get("role") == "user"
        ])
        logger.info(f"Recent user text for matching: {recent_user_text[:100]}...")

        for prop in search_results:
            name_lower = prop.get("project_name", "").lower()
            name_words = [w for w in name_lower.split() if len(w) > 2]
            if any(word in recent_user_text for word in name_words):
                state["selected_project_id"] = prop["id"]
                logger.info(f"Matched property: {prop['project_name']} (id={prop['id']})")
                break

    # Check if we have enough info to proceed (first_name + email required; last_name is optional)
    if validated_lead_data.get("first_name") and validated_lead_data.get("email"):
        state["lead_captured"] = True
        state["tools_used"] = state.get("tools_used", []) + ["booking_tool"]

        # Save lead using BookingTool
        try:
            booking_tool = get_booking_tool()
            lead = await booking_tool.upsert_lead(
                conversation_id=state["conversation_id"],
                lead_data=validated_lead_data,
                preferences=state.get("preferences", {})
            )
            state["lead_id"] = lead.id
            logger.info(f"Lead saved via BookingTool: {lead.id}")
        except Exception as e:
            logger.error(f"Error saving lead: {e}")

        return state

    # Determine what's missing for followup (name + email required; last_name optional)
    missing = []
    if not validated_lead_data.get("first_name"):
        missing.append("name")
    if not validated_lead_data.get("email"):
        missing.append("email address")

    # Ask for missing info
    try:
        followup_prompt = ChatPromptTemplate.from_template(LEAD_FOLLOWUP_PROMPT)
        chain = followup_prompt | llm

        response = await chain.ainvoke({
            "lead_info": json.dumps(validated_lead_data),
            "missing_info": ", ".join(missing),
            "user_message": user_message
        })

        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })

    except Exception as e:
        logger.error(f"Error generating followup: {e}")

        if not validated_lead_data.get("first_name"):
            msg = "Could you share your name?"
        elif not validated_lead_data.get("email"):
            first_name = validated_lead_data.get("first_name", "")
            msg = f"Thanks {first_name}! What's your email address?"
        else:
            msg = "I just need a bit more information. What's your email address?"

        state["messages"].append({
            "role": "assistant",
            "content": msg
        })

    return state
