"""
Unit tests for agent nodes.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from agent.state import create_initial_state


@pytest.mark.django_db
class TestPropertySearch:
    """Tests for property search node."""

    def test_build_search_query_with_city(self, sample_projects):
        """Test building search query with city."""
        from agent.nodes.property_search import build_search_query

        preferences = {"city": "Chicago"}
        query = build_search_query(preferences)

        projects = list(__import__('domain.models', fromlist=['Project']).Project.objects.filter(query))
        assert len(projects) >= 2
        assert all("Chicago" in p.city for p in projects)

    def test_build_search_query_with_bedrooms(self, sample_projects):
        """Test building search query with bedrooms."""
        from agent.nodes.property_search import build_search_query

        preferences = {"city": "Chicago", "bedrooms": 2}
        query = build_search_query(preferences)

        projects = list(__import__('domain.models', fromlist=['Project']).Project.objects.filter(query))
        assert len(projects) >= 1

    def test_calculate_match_score_perfect(self, sample_project):
        """Test match score calculation for perfect match."""
        from agent.nodes.property_search import calculate_match_score

        preferences = {
            "city": "Chicago",
            "bedrooms": 2,
            "budget_max": 900000,
        }

        score = calculate_match_score(sample_project, preferences)
        assert score >= 0.8

    def test_calculate_match_score_partial(self, sample_project):
        """Test match score calculation for partial match."""
        from agent.nodes.property_search import calculate_match_score

        preferences = {
            "city": "Chicago",
            "bedrooms": 3,  # Different from project's 2
            "budget_max": 500000,  # Below project price
        }

        score = calculate_match_score(sample_project, preferences)
        assert 0.2 <= score <= 0.7


@pytest.mark.django_db
class TestIntentClassifier:
    """Tests for intent classification."""

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_classify_greeting_intent(self, mock_llm):
        """Test classifying greeting intent."""
        from agent.nodes.intent_classifier import classify_intent

        mock_response = MagicMock()
        mock_response.content = "greeting"
        mock_llm.return_value.ainvoke = AsyncMock(return_value=mock_response)

        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Hello there!"}]

        # Mock the chain
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.intent_classifier.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await classify_intent(state)
            assert result["user_intent"] == "greeting"

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_classify_preference_intent(self, mock_llm):
        """Test classifying share_preferences intent."""
        from agent.nodes.intent_classifier import classify_intent

        mock_response = MagicMock()
        mock_response.content = "share_preferences"
        mock_llm.return_value.ainvoke = AsyncMock(return_value=mock_response)

        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "I'm looking for a 2 bedroom apartment in Chicago"}
        ]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.intent_classifier.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await classify_intent(state)
            assert result["user_intent"] == "share_preferences"


@pytest.mark.django_db
class TestLeadCapture:
    """Tests for lead capture node."""

    def test_extract_email(self):
        """Test email extraction from text."""
        from agent.nodes.lead_capture import extract_email

        text = "My email is john.doe@example.com"
        email = extract_email(text)
        assert email == "john.doe@example.com"

    def test_extract_email_no_match(self):
        """Test email extraction with no email."""
        from agent.nodes.lead_capture import extract_email

        text = "I don't have an email"
        email = extract_email(text)
        assert email == ""

    def test_extract_phone(self):
        """Test phone extraction from text."""
        from agent.nodes.lead_capture import extract_phone

        text = "Call me at +1-555-123-4567"
        phone = extract_phone(text)
        assert "555" in phone


@pytest.mark.django_db
class TestQuestionAnswering:
    """Tests for question answering node with web search fallback."""

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    @patch('agent.nodes.question_answering.get_tavily_tool')
    @patch('agent.nodes.question_answering.should_search_web')
    async def test_answer_without_web_search(self, mock_should_search, mock_get_tavily, mock_llm):
        """Test answering without web search when not needed."""
        from agent.nodes.question_answering import answer_questions
        from agent.state import create_initial_state

        # Configure mocks
        mock_should_search.return_value = False

        mock_response = MagicMock()
        mock_response.content = "This apartment has 2 bedrooms and costs $500,000."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.question_answering.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            state = create_initial_state("test-123")
            state["messages"] = [
                {"role": "user", "content": "What is the price of this apartment?"}
            ]
            state["search_results"] = [
                {"project_name": "Test Project", "city": "Chicago", "price_usd": 500000}
            ]

            result = await answer_questions(state)

            # Web search should not be called
            mock_get_tavily.assert_not_called()

            # Response should be added
            assert len(result["messages"]) == 2
            assert result["messages"][-1]["role"] == "assistant"

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    @patch('agent.nodes.question_answering.get_tavily_tool')
    @patch('agent.nodes.question_answering.should_search_web')
    async def test_answer_with_web_search_fallback(self, mock_should_search, mock_get_tavily, mock_llm):
        """Test answering with web search fallback for external info."""
        from agent.nodes.question_answering import answer_questions
        from agent.state import create_initial_state

        # Configure mocks
        mock_should_search.return_value = True

        mock_tavily = MagicMock()
        mock_tavily.is_available.return_value = True
        mock_tavily.search = AsyncMock(return_value={
            "success": True,
            "answer": "There are several good schools nearby.",
            "results": [
                {"title": "Lincoln School", "content": "Great public school", "url": "http://example.com"}
            ]
        })
        mock_get_tavily.return_value = mock_tavily

        mock_response = MagicMock()
        mock_response.content = "Based on my search, there are several good schools nearby including Lincoln School."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.question_answering.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            state = create_initial_state("test-123")
            state["messages"] = [
                {"role": "user", "content": "What schools are near this property?"}
            ]
            state["search_results"] = [
                {"project_name": "Test Project", "city": "Chicago"}
            ]
            state["tools_used"] = []

            result = await answer_questions(state)

            # Web search should be called
            mock_tavily.search.assert_called_once()

            # tavily_search should be in tools_used
            assert "tavily_search" in result["tools_used"]

            # Response should be added
            assert len(result["messages"]) == 2
            assert result["messages"][-1]["role"] == "assistant"

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    @patch('agent.nodes.question_answering.get_tavily_tool')
    @patch('agent.nodes.question_answering.should_search_web')
    async def test_answer_web_search_unavailable(self, mock_should_search, mock_get_tavily, mock_llm):
        """Test fallback when web search is not available."""
        from agent.nodes.question_answering import answer_questions
        from agent.state import create_initial_state

        # Configure mocks
        mock_should_search.return_value = True

        mock_tavily = MagicMock()
        mock_tavily.is_available.return_value = False
        mock_get_tavily.return_value = mock_tavily

        mock_response = MagicMock()
        mock_response.content = "I don't have specific information about schools nearby."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.question_answering.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            state = create_initial_state("test-123")
            state["messages"] = [
                {"role": "user", "content": "What schools are nearby?"}
            ]
            state["tools_used"] = []

            result = await answer_questions(state)

            # Search method should not be called when unavailable
            mock_tavily.search.assert_not_called()

            # Response should still be added
            assert len(result["messages"]) == 2
