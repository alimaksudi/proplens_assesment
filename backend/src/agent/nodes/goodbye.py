"""
Goodbye node for ending conversations gracefully.
"""

from agent.state import ConversationState


async def handle_goodbye(state: ConversationState) -> ConversationState:
    """
    Handle goodbye messages and end the conversation gracefully.

    Generates an appropriate farewell message based on conversation context.
    """
    state["current_node"] = "goodbye"

    # Check if booking was just confirmed - give a different message
    if state.get("booking_confirmed"):
        message = "You're all set! We'll be in touch soon about your viewing. Have a wonderful day!"
    else:
        message = "Thank you for exploring properties with Silver Land! Feel free to return whenever you're ready. Have a great day!"

    state["messages"].append({
        "role": "assistant",
        "content": message
    })

    return state
