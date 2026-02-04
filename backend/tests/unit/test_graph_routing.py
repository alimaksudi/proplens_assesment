"""
Unit tests for graph routing logic.

Tests the _route_after_classification, _should_search_properties,
_after_question, and _lead_capture_complete routing functions.
"""

import pytest
from unittest.mock import patch, MagicMock

from agent.state import create_initial_state
from agent.graph import PropertyAgentGraph


@pytest.fixture
def agent_graph():
    """Create agent graph for testing routing logic."""
    with patch('agent.graph.ChatOpenAI'):
        graph = PropertyAgentGraph()
        return graph


class TestRouteAfterClassification:
    """Tests for _route_after_classification routing."""

    def test_route_greeting_intent(self, agent_graph):
        """RT-01: Greeting intent routes to discover."""
        state = create_initial_state("test-123")
        state["user_intent"] = "greeting"

        result = agent_graph._route_after_classification(state)
        assert result == "discover"

    def test_route_share_preferences_intent(self, agent_graph):
        """RT-02: Share preferences intent routes to discover."""
        state = create_initial_state("test-123")
        state["user_intent"] = "share_preferences"

        result = agent_graph._route_after_classification(state)
        assert result == "discover"

    def test_route_ask_question_intent(self, agent_graph):
        """RT-03: Ask question intent routes to question."""
        state = create_initial_state("test-123")
        state["user_intent"] = "ask_question"

        result = agent_graph._route_after_classification(state)
        assert result == "question"

    def test_route_request_recommendations_with_complete_prefs(self, agent_graph):
        """RT-04: Request recommendations with preferences_complete routes to search."""
        state = create_initial_state("test-123")
        state["user_intent"] = "request_recommendations"
        state["preferences_complete"] = True

        result = agent_graph._route_after_classification(state)
        assert result == "search"

    def test_route_request_recommendations_with_city(self, agent_graph):
        """RT-05: Request recommendations with city routes to search."""
        state = create_initial_state("test-123")
        state["user_intent"] = "request_recommendations"
        state["preferences"] = {"city": "Chicago"}

        result = agent_graph._route_after_classification(state)
        assert result == "search"

    def test_route_request_recommendations_no_prefs(self, agent_graph):
        """RT-06: Request recommendations without city/prefs routes to discover."""
        state = create_initial_state("test-123")
        state["user_intent"] = "request_recommendations"
        state["preferences"] = {}

        result = agent_graph._route_after_classification(state)
        assert result == "discover"

    def test_route_express_interest_with_results(self, agent_graph):
        """RT-07: Express interest with search results routes to booking."""
        state = create_initial_state("test-123")
        state["user_intent"] = "express_interest"
        state["search_results"] = [{"id": "123", "project_name": "Test"}]

        result = agent_graph._route_after_classification(state)
        assert result == "booking"

    def test_route_express_interest_no_results(self, agent_graph):
        """RT-08: Express interest without results routes to recommend."""
        state = create_initial_state("test-123")
        state["user_intent"] = "express_interest"
        state["search_results"] = []

        result = agent_graph._route_after_classification(state)
        assert result == "recommend"

    def test_route_book_viewing_intent(self, agent_graph):
        """RT-09: Book viewing intent routes to booking."""
        state = create_initial_state("test-123")
        state["user_intent"] = "book_viewing"

        result = agent_graph._route_after_classification(state)
        assert result == "booking"

    def test_route_provide_contact_intent(self, agent_graph):
        """RT-10: Provide contact intent routes to provide_contact."""
        state = create_initial_state("test-123")
        state["user_intent"] = "provide_contact"

        result = agent_graph._route_after_classification(state)
        assert result == "provide_contact"

    def test_route_goodbye_intent(self, agent_graph):
        """RT-11: Goodbye intent routes to goodbye node."""
        state = create_initial_state("test-123")
        state["user_intent"] = "goodbye"

        result = agent_graph._route_after_classification(state)
        assert result == "goodbye"

    def test_route_clarify_intent(self, agent_graph):
        """RT-12: Clarify intent routes to question."""
        state = create_initial_state("test-123")
        state["user_intent"] = "clarify"

        result = agent_graph._route_after_classification(state)
        assert result == "question"

    def test_route_other_with_context(self, agent_graph):
        """RT-13: Other intent with conversation context routes to question."""
        state = create_initial_state("test-123")
        state["user_intent"] = "other"
        state["messages"] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
            {"role": "user", "content": "Something random"},
        ]

        result = agent_graph._route_after_classification(state)
        assert result == "question"

    def test_route_other_with_city(self, agent_graph):
        """RT-14: Other intent with city but no context routes to search."""
        state = create_initial_state("test-123")
        state["user_intent"] = "other"
        state["preferences"] = {"city": "Chicago"}
        state["messages"] = [{"role": "user", "content": "test"}]

        result = agent_graph._route_after_classification(state)
        assert result == "search"

    def test_route_other_no_context_no_city(self, agent_graph):
        """RT-15: Other intent without context or city routes to discover."""
        state = create_initial_state("test-123")
        state["user_intent"] = "other"
        state["preferences"] = {}
        state["messages"] = [{"role": "user", "content": "test"}]

        result = agent_graph._route_after_classification(state)
        assert result == "discover"

    def test_route_with_error_message(self, agent_graph):
        """RT-16: Any intent with error_message routes to error."""
        state = create_initial_state("test-123")
        state["user_intent"] = "greeting"
        state["error_message"] = "Something went wrong"

        result = agent_graph._route_after_classification(state)
        assert result == "error"


class TestShouldSearchProperties:
    """Tests for _should_search_properties routing."""

    def test_search_with_city_and_bedrooms(self, agent_graph):
        """RT-SS01: City + bedrooms should trigger search."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "bedrooms": 2}

        result = agent_graph._should_search_properties(state)
        assert result == "search"

    def test_search_with_city_and_budget(self, agent_graph):
        """RT-SS02: City + budget should trigger search."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_max": 500000}

        result = agent_graph._should_search_properties(state)
        assert result == "search"

    def test_search_with_city_and_complete_flag(self, agent_graph):
        """RT-SS03: City + preferences_complete should trigger search."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago"}
        state["preferences_complete"] = True

        result = agent_graph._should_search_properties(state)
        assert result == "search"

    def test_no_search_city_only_incomplete(self, agent_graph):
        """RT-SS04: City only without complete flag should continue."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago"}
        state["preferences_complete"] = False

        result = agent_graph._should_search_properties(state)
        assert result == "continue"

    def test_no_search_bedrooms_only(self, agent_graph):
        """RT-SS05: Bedrooms only without city should continue."""
        state = create_initial_state("test-123")
        state["preferences"] = {"bedrooms": 2}

        result = agent_graph._should_search_properties(state)
        assert result == "continue"

    def test_search_with_all_preferences(self, agent_graph):
        """RT-SS06: City + bedrooms + budget + complete should search."""
        state = create_initial_state("test-123")
        state["preferences"] = {
            "city": "Chicago",
            "bedrooms": 2,
            "budget_max": 500000
        }
        state["preferences_complete"] = True

        result = agent_graph._should_search_properties(state)
        assert result == "search"

    def test_search_with_budget_min(self, agent_graph):
        """City + budget_min should trigger search."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_min": 100000}

        result = agent_graph._should_search_properties(state)
        assert result == "search"


class TestAfterQuestionRouting:
    """Tests for _after_question routing."""

    def test_route_to_booking_on_book_keyword(self, agent_graph):
        """RT-AQ01: Message with 'book' routes to booking."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "I want to book a viewing"}
        ]

        result = agent_graph._after_question(state)
        assert result == "booking"

    def test_route_to_booking_on_schedule_keyword(self, agent_graph):
        """Message with 'schedule' routes to booking."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "Can I schedule a visit?"}
        ]

        result = agent_graph._after_question(state)
        assert result == "booking"

    def test_route_to_search_on_show_more(self, agent_graph):
        """RT-AQ02: Message with 'show me' routes to search."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "Show me more options"}
        ]

        result = agent_graph._after_question(state)
        assert result == "search"

    def test_route_to_search_on_other_options(self, agent_graph):
        """RT-AQ03: Message with 'other options' routes to search."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "Any other options?"}
        ]

        result = agent_graph._after_question(state)
        assert result == "search"

    def test_route_to_end_on_regular_question(self, agent_graph):
        """RT-AQ04: Regular question routes to end."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "What are the amenities?"}
        ]

        result = agent_graph._after_question(state)
        assert result == "end"

    def test_route_to_end_on_empty_messages(self, agent_graph):
        """Empty messages routes to end."""
        state = create_initial_state("test-123")
        state["messages"] = []

        result = agent_graph._after_question(state)
        assert result == "end"


class TestLeadCaptureComplete:
    """Tests for _lead_capture_complete routing."""

    def test_confirm_with_complete_data(self, agent_graph):
        """RT-LC01: Complete lead data + project_id routes to confirm."""
        state = create_initial_state("test-123")
        state["lead_data"] = {
            "first_name": "John",
            # last_name is optional - only first_name + email required
            "email": "john@example.com"
        }
        state["selected_project_id"] = "project-123"

        result = agent_graph._lead_capture_complete(state)
        assert result == "confirm"

    def test_continue_with_first_name_only(self, agent_graph):
        """RT-LC02: First name only routes to continue."""
        state = create_initial_state("test-123")
        state["lead_data"] = {"first_name": "John"}
        state["selected_project_id"] = "project-123"

        result = agent_graph._lead_capture_complete(state)
        assert result == "continue"

    def test_continue_with_email_only(self, agent_graph):
        """RT-LC03: Email only routes to continue."""
        state = create_initial_state("test-123")
        state["lead_data"] = {"email": "john@example.com"}
        state["selected_project_id"] = "project-123"

        result = agent_graph._lead_capture_complete(state)
        assert result == "continue"

    def test_continue_without_project_id(self, agent_graph):
        """RT-LC04: Complete lead but no project_id routes to continue."""
        state = create_initial_state("test-123")
        state["lead_data"] = {
            "first_name": "John",
            # last_name is optional
            "email": "john@example.com"
        }
        state["selected_project_id"] = None

        result = agent_graph._lead_capture_complete(state)
        assert result == "continue"

    def test_continue_with_empty_lead_data(self, agent_graph):
        """Empty lead data routes to continue."""
        state = create_initial_state("test-123")
        state["lead_data"] = {}
        state["selected_project_id"] = "project-123"

        result = agent_graph._lead_capture_complete(state)
        assert result == "continue"

    def test_confirm_with_all_fields(self, agent_graph):
        """Complete lead data with all fields routes to confirm."""
        state = create_initial_state("test-123")
        state["lead_data"] = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        state["selected_project_id"] = "project-123"

        result = agent_graph._lead_capture_complete(state)
        assert result == "confirm"
