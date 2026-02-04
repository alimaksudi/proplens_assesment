"""
Unit tests for the preference discovery node.

Tests the discover_preferences function that extracts and tracks user preferences.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from agent.state import create_initial_state
from agent.nodes.preference_discovery import discover_preferences


@pytest.mark.django_db
class TestPreferenceDiscoveryNode:
    """Tests for preference discovery functionality."""

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_extract_city_and_bedrooms(self, mock_llm):
        """ND-PD01: Extract city and bedrooms from message."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "I'm looking for a 2-bedroom in Dubai"}
        ]

        # Mock LLM extraction response
        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"city": "Dubai", "bedrooms": 2}'

        # Mock LLM preference response
        mock_pref_response = MagicMock()
        mock_pref_response.content = "Great! You're looking for a 2-bedroom in Dubai. What's your budget?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["city"] == "Dubai"
            assert result["preferences"]["bedrooms"] == 2
            assert result["current_node"] == "discover_preferences"

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_extract_budget_max(self, mock_llm):
        """ND-PD02: Extract budget from message."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "Budget is $500,000"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"budget_max": 500000}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Good to know. Which city are you interested in?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["budget_max"] == 500000

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_extract_5_million_budget(self, mock_llm):
        """ND-PD03: Extract 5 million budget."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "5 million budget"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"budget_max": 5000000}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Noted. Where are you looking?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["budget_max"] == 5000000

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_extract_under_1_million(self, mock_llm):
        """ND-PD04: Extract 'under 1 million' budget."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "Under 1 million"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"budget_max": 1000000}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Got it. What city?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["budget_max"] == 1000000

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_replace_city_with_new(self, mock_llm):
        """ND-PD05: New city replaces old city."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Dubai", "bedrooms": 2}
        state["messages"] = [
            {"role": "user", "content": "What about Chicago instead?"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"city": "Chicago", "country": "US"}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Switching to Chicago. Let me search for properties."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["city"] == "Chicago"
            assert result["preferences"]["country"] == "US"
            # bedrooms should still be preserved
            assert result["preferences"]["bedrooms"] == 2

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_clear_budget_dont_care_about_price(self, mock_llm):
        """ND-PD06: 'Don't care about price' clears budget."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_max": 500000}
        state["messages"] = [
            {"role": "user", "content": "Don't care about price"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"clear_budget": true}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "No budget constraint. Let me search for you."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            # Budget should be cleared
            assert "budget_max" not in result["preferences"]
            assert "budget_min" not in result["preferences"]
            # City should be preserved
            assert result["preferences"]["city"] == "Chicago"

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_clear_budget_any_price(self, mock_llm):
        """ND-PD07: 'Any price is fine' clears budget."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_min": 100000, "budget_max": 500000}
        state["messages"] = [
            {"role": "user", "content": "Any price is fine"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{}'  # LLM might not return clear_budget

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Okay, no budget limit."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            # Budget should be cleared by phrase detection
            assert "budget_max" not in result["preferences"]
            assert "budget_min" not in result["preferences"]

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_whatever_available_clears_budget_and_completes(self, mock_llm):
        """ND-PD08: 'Whatever available' clears budget and sets preferences_complete."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_max": 500000}
        state["messages"] = [
            {"role": "user", "content": "Whatever is available"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"clear_budget": true}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Searching all properties."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            # Budget should be cleared
            assert "budget_max" not in result["preferences"]
            # preferences_complete should be True (has city + user said no budget)
            assert result["preferences_complete"] is True

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_extract_large_budget_number(self, mock_llm):
        """ND-PD09: Extract 10000000 budget."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "10000000"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"budget_max": 10000000}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Budget noted. What city?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["budget_max"] == 10000000

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_extract_property_type_apartment(self, mock_llm):
        """ND-PD10: Extract 'apartment' property type."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "I want an apartment"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"property_type": "apartment"}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Looking for an apartment. What city?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["property_type"] == "apartment"

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_extract_villa_with_features(self, mock_llm):
        """ND-PD11: Extract 'villa with pool' - property type and features."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "I want a villa with pool"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"property_type": "villa", "features": ["pool"]}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "A villa with pool. Which city?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["property_type"] == "villa"
            assert "pool" in result["preferences"].get("features", [])

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_preferences_complete_with_city_and_bedrooms(self, mock_llm):
        """City + bedrooms marks preferences as complete."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "2-bedroom in Chicago"}
        ]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"city": "Chicago", "bedrooms": 2}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Searching..."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            assert result["preferences"]["city"] == "Chicago"
            assert result["preferences"]["bedrooms"] == 2
            assert result["preferences_complete"] is True

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_api_error_fallback(self, mock_llm):
        """API error returns fallback message."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "Hello"}
        ]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)

            # Should have fallback message
            assert len(result["messages"]) == 2
            assert result["messages"][-1]["role"] == "assistant"
            assert "help you find" in result["messages"][-1]["content"].lower()


class TestNoBudgetPhrases:
    """Tests for no budget phrase detection."""

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_no_budget_phrase_doesnt_matter(self, mock_llm):
        """'Doesn't matter' clears budget."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_max": 500000}
        state["messages"] = [{"role": "user", "content": "Price doesn't matter"}]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Okay!"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)
            assert "budget_max" not in result["preferences"]

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_no_budget_phrase_show_me_all(self, mock_llm):
        """'Show me all' clears budget."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_max": 500000}
        state["messages"] = [{"role": "user", "content": "Show me all properties"}]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Okay!"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)
            assert "budget_max" not in result["preferences"]

    @pytest.mark.asyncio
    @patch('agent.nodes.preference_discovery.ChatOpenAI')
    async def test_no_budget_phrase_just_show_me(self, mock_llm):
        """'Just show me' clears budget."""
        state = create_initial_state("test-123")
        state["preferences"] = {"city": "Chicago", "budget_max": 500000}
        state["messages"] = [{"role": "user", "content": "Just show me what you have"}]

        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{}'

        mock_pref_response = MagicMock()
        mock_pref_response.content = "Sure!"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=[mock_extraction_response, mock_pref_response])

        with patch('agent.nodes.preference_discovery.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await discover_preferences(state)
            assert "budget_max" not in result["preferences"]
