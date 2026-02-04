"""
Booking confirmation node for finalizing viewing appointments.

Uses BookingTool for centralized booking management.
"""

import logging
from agent.state import ConversationState
from agent.tools import get_booking_tool
from domain.models import Project, Lead

logger = logging.getLogger(__name__)


async def confirm_booking(state: ConversationState) -> ConversationState:
    """
    Create booking record and confirm with user.

    Uses BookingTool for consistent booking creation and message generation.
    """
    state["current_node"] = "confirm_booking"
    state["tools_used"] = state.get("tools_used", []) + ["booking_tool"]

    lead_id = state.get("lead_id")
    project_id = state.get("selected_project_id")
    conversation_id = state.get("conversation_id")

    if not lead_id or not project_id:
        lead_data = state.get("lead_data", {})

        # Determine what's actually missing and ask for the right thing
        if not lead_data.get("first_name"):
            message = "I'd love to help you book a viewing! Could you share your first name?"
        elif not lead_data.get("email"):
            first_name = lead_data.get("first_name", "")
            message = f"Thanks {first_name}! What's your email address so I can confirm the viewing?"
        elif not project_id:
            message = "I apologize, but I need a bit more information to complete your booking. Could you confirm which property you'd like to view?"
        else:
            message = "I apologize, but I need a bit more information to complete your booking. Could you confirm which property you'd like to view?"

        state["messages"].append({
            "role": "assistant",
            "content": message
        })
        return state

    booking_tool = get_booking_tool()

    try:
        # Create booking using BookingTool
        notes = f"Booking from chat conversation. Preferences: {state.get('preferences', {})}"
        booking = await booking_tool.create_booking(
            lead_id=lead_id,
            project_id=project_id,
            conversation_id=conversation_id,
            notes=notes
        )

        state["booking_id"] = booking.id
        state["booking_confirmed"] = True

        # Generate confirmation message using BookingTool
        confirmation = await booking_tool.get_booking_confirmation_message(booking)

        state["messages"].append({
            "role": "assistant",
            "content": confirmation
        })

        logger.info(f"Booking created: {booking.id} for project {project_id}")

    except ValueError as e:
        # Invalid project ID
        logger.error(f"Invalid project: {e}")
        state["messages"].append({
            "role": "assistant",
            "content": "I apologize, but I couldn't find that property. Could you let me know which property you'd like to view?"
        })

    except Lead.DoesNotExist:
        logger.error(f"Lead not found: {lead_id}")
        state["messages"].append({
            "role": "assistant",
            "content": "I need your contact information to complete the booking. Could you share your email address?"
        })

    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        state["messages"].append({
            "role": "assistant",
            "content": "I apologize, but there was an issue completing your booking. Please try again or contact us directly at support@silverlandproperties.com."
        })

    return state
