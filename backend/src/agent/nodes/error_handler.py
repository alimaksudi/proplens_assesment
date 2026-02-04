"""
Error handler node for graceful error recovery.
"""

import logging
from agent.state import ConversationState

logger = logging.getLogger(__name__)


async def handle_error(state: ConversationState) -> ConversationState:
    """
    Handle errors gracefully and provide helpful response.
    """
    state["current_node"] = "handle_error"

    error_message = state.get("error_message", "")
    retry_count = state.get("retry_count", 0)

    logger.warning(f"Error handler invoked. Error: {error_message}, Retry: {retry_count}")

    # Increment retry count
    state["retry_count"] = retry_count + 1

    # Clear error for retry
    state["error_message"] = None

    if retry_count >= 3:
        state["messages"].append({
            "role": "assistant",
            "content": "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment, or contact our team directly at support@silverlandproperties.com for immediate assistance."
        })
    else:
        # Provide contextual recovery
        current_node = state.get("current_node", "")

        if "search" in current_node or "recommend" in current_node:
            msg = "I had trouble searching for properties. Could you tell me again what you're looking for?"
        elif "booking" in current_node or "lead" in current_node:
            msg = "I had an issue processing your booking request. Could you provide your details again?"
        else:
            msg = "I apologize for the confusion. Could you repeat what you're looking for? I'm here to help you find the perfect property."

        state["messages"].append({
            "role": "assistant",
            "content": msg
        })

    return state
