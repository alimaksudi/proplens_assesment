"""
Booking proposal node for initiating viewing requests.
"""

import json
import logging
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.config import get_fallback_message
from agent.prompts import BOOKING_PROPOSAL_PROMPT
from agent.utils.llm import get_conversational_llm

logger = logging.getLogger(__name__)


async def propose_booking(state: ConversationState) -> ConversationState:
    """
    Propose booking a property viewing and initiate lead capture.
    """
    state["current_node"] = "propose_booking"

    messages = state.get("messages", [])
    search_results = state.get("search_results", [])

    # Get user message
    user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            user_message = msg["content"]
            break

    # Try to identify which property they're interested in
    if search_results:
        # Default to first result if not specified
        state["selected_project_id"] = search_results[0]["id"]

        # Check ALL recent user messages for property mentions (not just current message)
        recent_user_messages = []
        for msg in messages[-6:]:  # Last 6 messages
            if msg["role"] == "user":
                recent_user_messages.append(msg["content"].lower())

        combined_user_text = " ".join(recent_user_messages)

        # Check if user mentioned a specific property
        for prop in search_results:
            name_lower = prop["project_name"].lower()
            # Match if any significant word from property name appears (skip short words like "the", "at")
            name_words = [w for w in name_lower.split() if len(w) > 2]
            if any(word in combined_user_text for word in name_words):
                state["selected_project_id"] = prop["id"]
                break

    # Format properties for context
    properties = []
    for prop in search_results[:3]:
        properties.append({
            "name": prop["project_name"],
            "city": prop["city"],
            "price": f"${prop['price_usd']:,.0f}" if prop.get("price_usd") else "Price on request"
        })

    llm = get_conversational_llm()

    prompt = ChatPromptTemplate.from_template(BOOKING_PROPOSAL_PROMPT)

    try:
        chain = prompt | llm
        response = await chain.ainvoke({
            "properties": json.dumps(properties),
            "user_message": user_message
        })

        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })

    except Exception as e:
        logger.error(f"Error in booking proposal: {e}")

        if search_results:
            prop = search_results[0]
            fallback = f"I'd be happy to arrange a viewing of {prop['project_name']} for you. To proceed, could you share your first name?"
        else:
            fallback = "I'd be happy to help you schedule a viewing. Could you share your first name so I can set this up?"

        state["messages"].append({
            "role": "assistant",
            "content": fallback
        })

    return state
