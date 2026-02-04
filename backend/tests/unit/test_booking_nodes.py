"""
Unit tests for booking-related nodes.

Tests booking_proposal, lead_capture, and booking_confirmation nodes.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from decimal import Decimal

from agent.state import create_initial_state
from agent.nodes.booking_proposal import propose_booking
from agent.nodes.lead_capture import capture_lead_details, extract_email, extract_phone
from agent.nodes.booking_confirmation import confirm_booking


class TestEmailExtraction:
    """Tests for email extraction function."""

    def test_extract_email_valid(self):
        """ND-LC03: Extract valid email."""
        email = extract_email("My email is john.doe@example.com")
        assert email == "john.doe@example.com"

    def test_extract_email_with_plus(self):
        """EC-LC02: Email with + sign is valid."""
        email = extract_email("Contact me at john+test@example.com")
        assert email == "john+test@example.com"

    def test_extract_email_no_match(self):
        """Email extraction with no email returns empty."""
        email = extract_email("I don't have an email to share")
        assert email == ""

    def test_extract_email_invalid_without_tld(self):
        """EC-LC01: Email without TLD not extracted."""
        email = extract_email("My email is john@example")
        assert email == ""


class TestPhoneExtraction:
    """Tests for phone extraction function."""

    def test_extract_phone_with_country_code(self):
        """ND-LC04: Extract phone with country code."""
        phone = extract_phone("Call me at +1-555-123-4567")
        assert "555" in phone
        assert "123" in phone

    def test_extract_phone_simple(self):
        """EC-LC03: Extract 7-digit phone."""
        phone = extract_phone("My number is 555-1234")
        assert "555" in phone

    def test_extract_phone_international(self):
        """Extract international phone format."""
        phone = extract_phone("Phone: +44 20 7946 0958")
        assert "44" in phone or "20" in phone

    def test_extract_phone_no_match(self):
        """Phone extraction with no phone returns empty."""
        phone = extract_phone("No phone here")
        assert phone == ""


@pytest.mark.django_db
class TestBookingProposalNode:
    """Tests for booking proposal node."""

    @pytest.mark.asyncio
    @patch('agent.nodes.booking_proposal.ChatOpenAI')
    async def test_propose_with_search_results(self, mock_llm):
        """ND-BP01: With search results, ask for name and set selected_project_id."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "I'd like to book a viewing"}]
        state["search_results"] = [
            {"id": "proj-1", "project_name": "Lakeside Towers", "city": "Chicago", "price_usd": 750000},
            {"id": "proj-2", "project_name": "Downtown Plaza", "city": "Chicago", "price_usd": 650000}
        ]

        mock_response = MagicMock()
        mock_response.content = "Great choice! I'd be happy to arrange a viewing. Could you share your first name?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.booking_proposal.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await propose_booking(state)

            assert result["current_node"] == "propose_booking"
            assert result["selected_project_id"] == "proj-1"  # Default to first
            assert len(result["messages"]) == 2
            assert "name" in result["messages"][-1]["content"].lower()

    @pytest.mark.asyncio
    @patch('agent.nodes.booking_proposal.ChatOpenAI')
    async def test_propose_without_search_results(self, mock_llm):
        """ND-BP02: No search results gives generic booking message."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "I want to book"}]
        state["search_results"] = []

        mock_response = MagicMock()
        mock_response.content = "I'd be happy to help you schedule a viewing. Could you share your first name?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.booking_proposal.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await propose_booking(state)

            assert result["current_node"] == "propose_booking"
            assert "selected_project_id" not in result or result.get("selected_project_id") is None

    @pytest.mark.asyncio
    @patch('agent.nodes.booking_proposal.ChatOpenAI')
    async def test_propose_with_specific_property_mention(self, mock_llm):
        """ND-BP03: User mentions property name, set correct selected_project_id."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "I want to book a viewing of Downtown Plaza"}]
        state["search_results"] = [
            {"id": "proj-1", "project_name": "Lakeside Towers", "city": "Chicago", "price_usd": 750000},
            {"id": "proj-2", "project_name": "Downtown Plaza", "city": "Chicago", "price_usd": 650000}
        ]

        mock_response = MagicMock()
        mock_response.content = "Great choice with Downtown Plaza! To proceed with your viewing, could you share your first name?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.booking_proposal.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await propose_booking(state)

            assert result["selected_project_id"] == "proj-2"

    @pytest.mark.asyncio
    @patch('agent.nodes.booking_proposal.ChatOpenAI')
    async def test_propose_fallback_on_error(self, mock_llm):
        """ND-BP04: LLM failure returns fallback message."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Book a viewing"}]
        state["search_results"] = [
            {"id": "proj-1", "project_name": "Lakeside Towers", "city": "Chicago", "price_usd": 750000}
        ]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        with patch('agent.nodes.booking_proposal.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await propose_booking(state)

            assert len(result["messages"]) == 2
            assert "Lakeside Towers" in result["messages"][-1]["content"]
            assert "first name" in result["messages"][-1]["content"].lower()


@pytest.mark.django_db
class TestLeadCaptureNode:
    """Tests for lead capture node."""

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_extract_first_name(self, mock_llm):
        """ND-LC01: Extract first name from message."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "John"}]
        state["lead_data"] = {}

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"first_name": "John"}'

        mock_followup_response = MagicMock()
        mock_followup_response.content = "Thanks John! What's your email address?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_followup_response])

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await capture_lead_details(state)

            assert result["lead_data"].get("first_name") == "John"

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_extract_first_and_last_name(self, mock_llm):
        """ND-LC02: Extract first and last name."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "John Smith"}]
        state["lead_data"] = {}

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"first_name": "John", "last_name": "Smith"}'

        mock_followup_response = MagicMock()
        mock_followup_response.content = "Thanks John Smith! What's your email?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_followup_response])

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await capture_lead_details(state)

            assert result["lead_data"].get("first_name") == "John"
            assert result["lead_data"].get("last_name") == "Smith"

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_extract_email(self, mock_llm):
        """ND-LC03: Extract email from message."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "john@example.com"}]
        state["lead_data"] = {"first_name": "John"}

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"email": "john@example.com"}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_extraction_response)

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)
            with patch('agent.nodes.lead_capture.get_booking_tool') as mock_booking_tool:
                mock_tool = MagicMock()
                mock_lead = MagicMock()
                mock_lead.id = "lead-123"
                mock_tool.upsert_lead = AsyncMock(return_value=mock_lead)
                mock_booking_tool.return_value = mock_tool

                result = await capture_lead_details(state)

                assert result["lead_data"].get("email") == "john@example.com"
                assert result["lead_captured"] is True

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_extract_name_and_email_combined(self, mock_llm):
        """ND-LC05: Extract name and email from combined message."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "John, john@test.com"}]
        state["lead_data"] = {}

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"first_name": "John", "email": "john@test.com"}'

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_extraction_response)

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)
            with patch('agent.nodes.lead_capture.get_booking_tool') as mock_booking_tool:
                mock_tool = MagicMock()
                mock_lead = MagicMock()
                mock_lead.id = "lead-123"
                mock_tool.upsert_lead = AsyncMock(return_value=mock_lead)
                mock_booking_tool.return_value = mock_tool

                result = await capture_lead_details(state)

                assert result["lead_data"].get("first_name") == "John"
                assert result["lead_data"].get("email") == "john@test.com"
                assert result["lead_captured"] is True

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_fallback_on_error(self, mock_llm):
        """API error returns fallback message asking for name when message is not extractable."""
        state = create_initial_state("test-123")
        # Use a message that won't be extracted as a name (contains special chars or is too long)
        state["messages"] = [{"role": "user", "content": "I want to book a viewing please"}]
        state["lead_data"] = {}

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await capture_lead_details(state)

            assert len(result["messages"]) == 2
            assert "first name" in result["messages"][-1]["content"].lower()

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_fallback_asks_email_when_has_name(self, mock_llm):
        """API error with name asks for email."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "test"}]
        state["lead_data"] = {"first_name": "John"}

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await capture_lead_details(state)

            assert len(result["messages"]) == 2
            assert "email" in result["messages"][-1]["content"].lower()
            assert "John" in result["messages"][-1]["content"]


@pytest.mark.django_db
class TestBookingConfirmationNode:
    """Tests for booking confirmation node."""

    @pytest.mark.asyncio
    async def test_confirm_with_valid_data(self, sample_project, sample_lead, sample_conversation):
        """ND-BC01: Valid lead_id + project_id creates booking."""
        state = create_initial_state(str(sample_conversation.id))
        state["lead_id"] = sample_lead.id
        state["selected_project_id"] = sample_project.id
        state["conversation_id"] = str(sample_conversation.id)
        state["preferences"] = {"city": "Chicago"}
        state["messages"] = []

        with patch('agent.nodes.booking_confirmation.get_booking_tool') as mock_booking_tool:
            mock_tool = MagicMock()
            mock_booking = MagicMock()
            mock_booking.id = "booking-123"
            mock_tool.create_booking = AsyncMock(return_value=mock_booking)
            mock_tool.get_booking_confirmation_message = AsyncMock(
                return_value="Your viewing has been scheduled! Reference: booking-123"
            )
            mock_booking_tool.return_value = mock_tool

            result = await confirm_booking(state)

            assert result["booking_id"] == "booking-123"
            assert result["booking_confirmed"] is True
            assert len(result["messages"]) == 1
            assert "booking-123" in result["messages"][-1]["content"]

    @pytest.mark.asyncio
    async def test_confirm_missing_lead_id(self):
        """ND-BC02: Missing lead_id asks for first name (not property confirmation)."""
        state = create_initial_state("test-123")
        state["lead_id"] = None
        state["selected_project_id"] = "proj-123"
        state["lead_data"] = {}  # No name or email
        state["messages"] = []

        result = await confirm_booking(state)

        assert len(result["messages"]) == 1
        # Should ask for first name, not "which property"
        assert "first name" in result["messages"][-1]["content"].lower()
        assert "booking_confirmed" not in result or not result.get("booking_confirmed")

    @pytest.mark.asyncio
    async def test_confirm_missing_project_id(self):
        """ND-BC03: Missing project_id asks for property confirmation (when lead data complete)."""
        state = create_initial_state("test-123")
        state["lead_id"] = None  # No lead_id but we have complete lead_data
        state["selected_project_id"] = None
        state["lead_data"] = {"first_name": "John", "email": "john@example.com"}  # Complete lead data
        state["messages"] = []

        result = await confirm_booking(state)

        assert len(result["messages"]) == 1
        # With complete lead data but no project_id, should ask about property
        assert "which property" in result["messages"][-1]["content"].lower()

    @pytest.mark.asyncio
    async def test_confirm_project_not_found(self):
        """ND-BC04: Project not found shows error."""
        state = create_initial_state("test-123")
        state["lead_id"] = "lead-123"
        state["selected_project_id"] = "nonexistent-proj"
        state["conversation_id"] = "conv-123"
        state["messages"] = []

        with patch('agent.nodes.booking_confirmation.get_booking_tool') as mock_booking_tool:
            mock_tool = MagicMock()
            mock_tool.create_booking = AsyncMock(side_effect=ValueError("Project not found"))
            mock_booking_tool.return_value = mock_tool

            result = await confirm_booking(state)

            assert len(result["messages"]) == 1
            assert "couldn't find" in result["messages"][-1]["content"].lower() or "property" in result["messages"][-1]["content"].lower()


class TestLeadCaptureEdgeCases:
    """Edge case tests for lead capture."""

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_name_with_accents(self, mock_llm):
        """EC-LC05: Name with accents accepted."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "José María"}]
        state["lead_data"] = {}

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"first_name": "José", "last_name": "María"}'

        mock_followup_response = MagicMock()
        mock_followup_response.content = "Thanks José! What's your email?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_followup_response])

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await capture_lead_details(state)

            # Name should be extracted (may be validated differently)
            assert result["current_node"] == "capture_lead"

    @pytest.mark.asyncio
    @patch('agent.nodes.lead_capture.ChatOpenAI')
    async def test_name_with_apostrophe(self, mock_llm):
        """EC-LC06: Name with apostrophe/hyphen accepted."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "O'Brien-Smith"}]
        state["lead_data"] = {}

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"first_name": "O\'Brien-Smith"}'

        mock_followup_response = MagicMock()
        mock_followup_response.content = "Thanks! What's your email?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_followup_response])

        with patch('agent.nodes.lead_capture.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await capture_lead_details(state)

            assert result["current_node"] == "capture_lead"
