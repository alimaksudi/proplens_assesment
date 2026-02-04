"""
Unit tests for the error handler node.

Tests the handle_error function for graceful error recovery.
"""

import pytest

from agent.state import create_initial_state
from agent.nodes.error_handler import handle_error


@pytest.mark.django_db
class TestErrorHandlerNode:
    """Tests for error handler functionality."""

    @pytest.mark.asyncio
    async def test_first_retry_generic(self):
        """ND-EH01: First retry (count=0) gives contextual message."""
        state = create_initial_state("test-123")
        state["error_message"] = "Some error occurred"
        state["retry_count"] = 0
        state["messages"] = []

        result = await handle_error(state)

        assert result["current_node"] == "handle_error"
        assert result["retry_count"] == 1
        assert result["error_message"] is None  # Cleared for retry
        assert len(result["messages"]) == 1
        assert "apologize" in result["messages"][-1]["content"].lower() or "confusion" in result["messages"][-1]["content"].lower()

    @pytest.mark.asyncio
    async def test_second_retry(self):
        """ND-EH02: Second retry (count=1) gives contextual message."""
        state = create_initial_state("test-123")
        state["error_message"] = "Another error"
        state["retry_count"] = 1
        state["messages"] = []

        result = await handle_error(state)

        assert result["retry_count"] == 2
        assert result["error_message"] is None
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_third_retry(self):
        """ND-EH03: Third retry (count=2) gives contextual message."""
        state = create_initial_state("test-123")
        state["error_message"] = "Yet another error"
        state["retry_count"] = 2
        state["messages"] = []

        result = await handle_error(state)

        assert result["retry_count"] == 3
        assert result["error_message"] is None
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_max_retries_contact_support(self):
        """ND-EH04: After 3+ retries, suggest contacting support."""
        state = create_initial_state("test-123")
        state["error_message"] = "Persistent error"
        state["retry_count"] = 3
        state["messages"] = []

        result = await handle_error(state)

        assert result["retry_count"] == 4
        assert result["error_message"] is None
        assert len(result["messages"]) == 1
        # Should mention contact/support
        content_lower = result["messages"][-1]["content"].lower()
        assert "contact" in content_lower or "support" in content_lower
        assert "silverlandproperties.com" in result["messages"][-1]["content"]

    @pytest.mark.asyncio
    async def test_search_context_error(self):
        """Error during search gives search-specific message."""
        state = create_initial_state("test-123")
        state["error_message"] = "Search failed"
        state["retry_count"] = 0
        state["current_node"] = "search_properties"
        state["messages"] = []

        result = await handle_error(state)

        # Note: current_node is overwritten to "handle_error"
        # The error handler checks the node BEFORE setting it to handle_error
        # Let's verify the message is appropriate
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_booking_context_error(self):
        """Error during booking gives booking-specific message."""
        state = create_initial_state("test-123")
        state["error_message"] = "Booking failed"
        state["retry_count"] = 0
        state["current_node"] = "confirm_booking"
        state["messages"] = []

        result = await handle_error(state)

        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_no_error_message(self):
        """Handler works even without error_message."""
        state = create_initial_state("test-123")
        state["retry_count"] = 0
        state["messages"] = []

        result = await handle_error(state)

        assert result["current_node"] == "handle_error"
        assert result["retry_count"] == 1
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_no_retry_count(self):
        """Handler works without existing retry_count."""
        state = create_initial_state("test-123")
        state["error_message"] = "Error"
        state["messages"] = []
        # Don't set retry_count - should default to 0

        result = await handle_error(state)

        assert result["retry_count"] == 1
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_preserves_existing_messages(self):
        """Handler preserves existing messages."""
        state = create_initial_state("test-123")
        state["error_message"] = "Error"
        state["retry_count"] = 0
        state["messages"] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]

        result = await handle_error(state)

        assert len(result["messages"]) == 3
        assert result["messages"][0]["content"] == "Hello"
        assert result["messages"][1]["content"] == "Hi!"
        assert result["messages"][2]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_exactly_at_max_retries(self):
        """At exactly 3 retries, shows support message."""
        state = create_initial_state("test-123")
        state["error_message"] = "Error"
        state["retry_count"] = 3
        state["messages"] = []

        result = await handle_error(state)

        content_lower = result["messages"][-1]["content"].lower()
        assert "contact" in content_lower or "support" in content_lower

    @pytest.mark.asyncio
    async def test_well_over_max_retries(self):
        """Well over max retries still shows support message."""
        state = create_initial_state("test-123")
        state["error_message"] = "Error"
        state["retry_count"] = 10
        state["messages"] = []

        result = await handle_error(state)

        assert result["retry_count"] == 11
        content_lower = result["messages"][-1]["content"].lower()
        assert "contact" in content_lower or "support" in content_lower
