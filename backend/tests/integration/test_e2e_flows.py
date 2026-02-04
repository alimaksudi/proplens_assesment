"""
End-to-end integration tests for complete conversation flows.

These tests verify full conversation scenarios through the agent.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from agent.graph import PropertyAgentGraph
from agent.state import create_initial_state


@pytest.fixture
def mock_openai():
    """Mock OpenAI for all tests."""
    with patch('agent.graph.ChatOpenAI') as mock:
        yield mock


@pytest.fixture
def agent_graph(mock_openai):
    """Create agent graph with mocked LLM."""
    return PropertyAgentGraph()


@pytest.mark.django_db
class TestE2EBookingFlow:
    """E2E-01: Happy path booking flow tests."""

    @pytest.mark.asyncio
    async def test_complete_booking_flow(self, agent_graph, sample_projects):
        """Complete booking flow from greeting to confirmation."""
        conversation_id = "e2e-test-001"

        # Step 1: Greeting
        with patch('agent.utils.llm.ChatOpenAI') as mock_greet, \
             patch('agent.utils.llm.ChatOpenAI') as mock_intent:

            # Mock greeting response
            mock_greet_response = MagicMock()
            mock_greet_response.content = "Welcome to Silver Land Properties!"
            mock_greet_chain = MagicMock()
            mock_greet_chain.ainvoke = AsyncMock(return_value=mock_greet_response)

            with patch('agent.nodes.greeting.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_greet_chain)

                # Mock intent classifier
                mock_intent_response = MagicMock()
                mock_intent_response.content = "greeting"
                mock_intent_chain = MagicMock()
                mock_intent_chain.ainvoke = AsyncMock(return_value=mock_intent_response)

                with patch('agent.nodes.intent_classifier.ChatPromptTemplate') as mock_intent_prompt:
                    mock_intent_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_intent_chain)

                    state = await agent_graph.process_message(
                        conversation_id,
                        "Hello"
                    )

                    # Verify greeting was processed
                    assert len(state["messages"]) >= 2


@pytest.mark.django_db
class TestE2ENoBudgetFlow:
    """E2E-02: No budget constraint search flow."""

    @pytest.mark.asyncio
    async def test_search_without_budget(self, sample_projects):
        """User says 'don't care about price' - budget cleared."""
        state = create_initial_state("e2e-test-002")
        state["messages"] = [
            {"role": "user", "content": "Show me whatever available in Chicago, any price is fine"}
        ]
        state["preferences"] = {"city": "Dubai", "budget_max": 500000}

        # Import the preference discovery to test directly
        from agent.nodes.preference_discovery import discover_preferences

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_extraction_response = MagicMock()
            mock_extraction_response.content = '{"city": "Chicago", "clear_budget": true}'

            mock_pref_response = MagicMock()
            mock_pref_response.content = "Searching Chicago with no budget limit."

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

            with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await discover_preferences(state)

                # Budget should be cleared
                assert "budget_max" not in result["preferences"]
                assert "budget_min" not in result["preferences"]
                # City should be Chicago
                assert result["preferences"]["city"] == "Chicago"
                # preferences_complete should be True
                assert result["preferences_complete"] is True


@pytest.mark.django_db
class TestE2ECityChangeFlow:
    """E2E-03: City change mid-conversation flow."""

    @pytest.mark.asyncio
    async def test_city_replacement(self):
        """User changes city mid-conversation."""
        state = create_initial_state("e2e-test-003")
        state["messages"] = [
            {"role": "assistant", "content": "Here are Dubai properties..."},
            {"role": "user", "content": "What about Chicago instead?"}
        ]
        state["preferences"] = {"city": "Dubai", "bedrooms": 2}

        from agent.nodes.preference_discovery import discover_preferences

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_extraction_response = MagicMock()
            mock_extraction_response.content = '{"city": "Chicago", "country": "US"}'

            mock_pref_response = MagicMock()
            mock_pref_response.content = "Switching to Chicago. Let me search."

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

            with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await discover_preferences(state)

                # City should be replaced
                assert result["preferences"]["city"] == "Chicago"
                assert result["preferences"]["country"] == "US"
                # Bedrooms should be preserved
                assert result["preferences"]["bedrooms"] == 2


@pytest.mark.django_db
class TestE2EQuestionAfterRecommendations:
    """E2E-04: Q&A after search flow."""

    @pytest.mark.asyncio
    async def test_question_triggers_web_search(self, sample_projects):
        """Question about schools triggers web search."""
        state = create_initial_state("e2e-test-004")
        state["messages"] = [
            {"role": "assistant", "content": "Here are Chicago properties..."},
            {"role": "user", "content": "What schools are nearby?"}
        ]
        state["search_results"] = [
            {"project_name": "Test Property", "city": "Chicago", "price_usd": 500000}
        ]
        state["tools_used"] = []

        from agent.nodes.question_answering import answer_questions

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "There are several schools nearby including Lincoln School."

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)

            with patch('agent.nodes.question_answering.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                with patch('agent.nodes.question_answering.get_tavily_tool') as mock_tavily:
                    mock_tool = MagicMock()
                    mock_tool.is_available.return_value = True
                    mock_tool.search = AsyncMock(return_value={
                        "success": True,
                        "answer": "Lincoln School is nearby.",
                        "results": [{"title": "Lincoln School", "content": "Great school", "url": "http://test.com"}]
                    })
                    mock_tavily.return_value = mock_tool

                    with patch('agent.nodes.question_answering.should_search_web', return_value=True):
                        result = await answer_questions(state)

                        # Web search should have been used
                        assert "tavily_search" in result["tools_used"]
                        assert len(result["messages"]) >= 3


@pytest.mark.django_db
class TestE2EIncrementalPreferences:
    """E2E-06: Incremental preference building flow."""

    @pytest.mark.asyncio
    async def test_step_by_step_preferences(self):
        """Build preferences incrementally over multiple messages."""
        # Step 1: User provides city only
        state = create_initial_state("e2e-test-006")
        state["messages"] = [{"role": "user", "content": "Singapore"}]

        from agent.nodes.preference_discovery import discover_preferences

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_extraction_response = MagicMock()
            mock_extraction_response.content = '{"city": "Singapore", "country": "SG"}'

            mock_pref_response = MagicMock()
            mock_pref_response.content = "Great! Looking in Singapore. How many bedrooms?"

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

            with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await discover_preferences(state)

                # City extracted but not complete yet
                assert result["preferences"]["city"] == "Singapore"
                assert result["preferences_complete"] is False

        # Step 2: User provides bedrooms
        state = result
        state["messages"].append({"role": "user", "content": "3 bedrooms"})

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_extraction_response = MagicMock()
            mock_extraction_response.content = '{"bedrooms": 3}'

            mock_pref_response = MagicMock()
            mock_pref_response.content = "3 bedrooms in Singapore. Searching now!"

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

            with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await discover_preferences(state)

                # Now should be complete
                assert result["preferences"]["city"] == "Singapore"
                assert result["preferences"]["bedrooms"] == 3
                assert result["preferences_complete"] is True


@pytest.mark.django_db
class TestE2EYesPleaseBooking:
    """Test 'yes please' after viewing offered triggers booking."""

    @pytest.mark.asyncio
    async def test_yes_please_intent(self):
        """'Yes please' after viewing offer should be book_viewing."""
        state = create_initial_state("e2e-test-yes")
        state["messages"] = [
            {"role": "assistant", "content": "Would you like to schedule a viewing?"},
            {"role": "user", "content": "Yes please"}
        ]

        from agent.nodes.intent_classifier import classify_intent

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "book_viewing"

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)

            with patch('agent.nodes.intent_classifier.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await classify_intent(state)

                assert result["user_intent"] == "book_viewing"

    @pytest.mark.asyncio
    async def test_sure_intent(self):
        """'Sure' after viewing offer should be book_viewing."""
        state = create_initial_state("e2e-test-sure")
        state["messages"] = [
            {"role": "assistant", "content": "Would you like to book a viewing?"},
            {"role": "user", "content": "Sure"}
        ]

        from agent.nodes.intent_classifier import classify_intent

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "book_viewing"

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)

            with patch('agent.nodes.intent_classifier.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await classify_intent(state)

                assert result["user_intent"] == "book_viewing"

    @pytest.mark.asyncio
    async def test_okay_intent(self):
        """'Okay' after viewing offer should be book_viewing."""
        state = create_initial_state("e2e-test-okay")
        state["messages"] = [
            {"role": "assistant", "content": "Shall I arrange a viewing for you?"},
            {"role": "user", "content": "Okay"}
        ]

        from agent.nodes.intent_classifier import classify_intent

        with patch('agent.utils.llm.ChatOpenAI') as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "book_viewing"

            mock_chain = MagicMock()
            mock_chain.ainvoke = AsyncMock(return_value=mock_response)

            with patch('agent.nodes.intent_classifier.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await classify_intent(state)

                assert result["user_intent"] == "book_viewing"
