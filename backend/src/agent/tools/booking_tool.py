"""
Booking tool for lead capture and booking management.
"""

import logging
from typing import Dict, Optional, Any
from asgiref.sync import sync_to_async
from domain.models import Lead, Booking, Project

logger = logging.getLogger(__name__)


class BookingTool:
    """
    Handle lead capture and booking creation.

    Provides methods for creating and updating leads, and creating
    property viewing bookings.
    """

    async def upsert_lead(
        self,
        conversation_id: str,
        lead_data: Dict[str, str],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Lead:
        """
        Create or update lead information.

        Args:
            conversation_id: Unique conversation ID
            lead_data: Dictionary with first_name, last_name, email, phone
            preferences: Optional dictionary of property preferences

        Returns:
            Lead object
        """
        try:
            # Use sync_to_async to wrap synchronous Django ORM operations
            @sync_to_async
            def _upsert():
                return Lead.objects.update_or_create(
                    conversation_id=conversation_id,
                    email=lead_data.get('email'),
                    defaults={
                        'first_name': lead_data.get('first_name'),
                        'last_name': lead_data.get('last_name'),
                        'phone': lead_data.get('phone'),
                        'preferences': preferences or {},
                        'lead_source': 'website_chat'
                    }
                )

            lead, created = await _upsert()

            action = "Created" if created else "Updated"
            logger.info(f"{action} lead: {lead.email}")

            return lead

        except Exception as e:
            logger.error(f"Failed to upsert lead: {e}")
            raise

    async def create_booking(
        self,
        lead_id: int,
        project_id: int,
        conversation_id: str,
        notes: Optional[str] = None
    ) -> Booking:
        """
        Create a property viewing booking.

        Args:
            lead_id: Lead database ID
            project_id: Project database ID
            conversation_id: Unique conversation ID
            notes: Optional booking notes

        Returns:
            Booking object
        """
        try:
            # Use sync_to_async to wrap synchronous Django ORM operations
            @sync_to_async
            def _get_project():
                return Project.objects.get(id=project_id)

            @sync_to_async
            def _create_booking(proj):
                return Booking.objects.create(
                    lead_id=lead_id,
                    project_id=project_id,
                    conversation_id=conversation_id,
                    status='pending',
                    notes=notes
                )

            project = await _get_project()
            booking = await _create_booking(project)

            logger.info(f"Created booking #{booking.id} for project {project.project_name}")

            return booking

        except Project.DoesNotExist:
            logger.error(f"Project {project_id} not found")
            raise ValueError(f"Invalid project ID: {project_id}")

        except Exception as e:
            logger.error(f"Failed to create booking: {e}")
            raise

    async def get_booking_confirmation_message(self, booking: Booking) -> str:
        """
        Generate booking confirmation message.

        Args:
            booking: Booking object

        Returns:
            Confirmation message string
        """
        # Use sync_to_async to wrap Django foreign key lookups
        @sync_to_async
        def _get_booking_details():
            return {
                'project_name': booking.project.project_name,
                'city': booking.project.city,
                'country': booking.project.country,
                'email': booking.lead.email
            }

        details = await _get_booking_details()

        message = f"""Your viewing has been scheduled.

Booking Details:
- Property: {details['project_name']}
- Location: {details['city']}, {details['country']}
- Confirmation sent to: {details['email']}

Our team will contact you within 24 hours to confirm the date and time of your viewing.

Is there anything else I can help you with?"""

        return message

    async def cancel_booking(self, booking_id: int) -> bool:
        """
        Cancel a booking.

        Args:
            booking_id: Booking database ID

        Returns:
            True if cancelled successfully
        """
        try:
            # Use sync_to_async to wrap synchronous Django ORM operations
            @sync_to_async
            def _cancel():
                b = Booking.objects.get(id=booking_id)
                b.status = 'cancelled'
                b.save()
                return True

            result = await _cancel()
            logger.info(f"Cancelled booking #{booking_id}")
            return result

        except Booking.DoesNotExist:
            logger.error(f"Booking {booking_id} not found")
            return False

        except Exception as e:
            logger.error(f"Failed to cancel booking: {e}")
            return False


# Singleton instance
_booking_tool_instance: Optional[BookingTool] = None


def get_booking_tool() -> BookingTool:
    """Get or create booking tool singleton."""
    global _booking_tool_instance

    if _booking_tool_instance is None:
        _booking_tool_instance = BookingTool()

    return _booking_tool_instance
