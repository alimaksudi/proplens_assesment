"""
Goodbye node for ending conversations gracefully.
"""

from agent.state import ConversationState
from agent.config import get_fallback_message


async def handle_goodbye(state: ConversationState) -> ConversationState:
    """
    Handle goodbye messages and end the conversation gracefully.

    Generates an appropriate farewell message based on conversation context.
    """
    state["current_node"] = "goodbye"

    # Check if booking was just confirmed - give a different message
    if state.get("booking_confirmed"):
        message = get_fallback_message("goodbye_after_booking")
    else:
        message = get_fallback_message("goodbye_general")

    state["messages"].append({
        "role": "assistant",
        "content": message
    })

    return state
