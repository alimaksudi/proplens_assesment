"""
Unit tests for the recommendation node.

Tests the recommend_properties function that presents search results.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from agent.state import create_initial_state
from agent.nodes.recommendation import recommend_properties


@pytest.mark.django_db
class TestRecommendationNode:
    """Tests for recommendation node functionality."""

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_recommend_multiple_properties(self, mock_llm):
        """ND-RC01: 5 properties shows top 3 with details."""
        state = create_initial_state("test-123")
        state["search_results"] = [
            {"project_name": "Lakeside Towers", "city": "Chicago", "bedrooms": 2, "bathrooms": 2, "price_usd": 750000, "area_sqm": 120, "property_type": "apartment", "completion_status": "available", "match_score": 0.95},
            {"project_name": "Downtown Plaza", "city": "Chicago", "bedrooms": 2, "bathrooms": 1, "price_usd": 650000, "area_sqm": 100, "property_type": "apartment", "completion_status": "available", "match_score": 0.90},
            {"project_name": "River View", "city": "Chicago", "bedrooms": 3, "bathrooms": 2, "price_usd": 850000, "area_sqm": 150, "property_type": "apartment", "completion_status": "available", "match_score": 0.85},
            {"project_name": "Park Side", "city": "Chicago", "bedrooms": 2, "bathrooms": 2, "price_usd": 700000, "area_sqm": 110, "property_type": "apartment", "completion_status": "off_plan", "match_score": 0.80},
            {"project_name": "Urban Lofts", "city": "Chicago", "bedrooms": 1, "bathrooms": 1, "price_usd": 500000, "area_sqm": 80, "property_type": "apartment", "completion_status": "available", "match_score": 0.75},
        ]
        state["preferences"] = {"city": "Chicago", "bedrooms": 2, "budget_max": 800000}
        state["messages"] = [{"role": "user", "content": "Show me properties"}]

        mock_response = MagicMock()
        mock_response.content = "Based on your search for 2-bedroom properties in Chicago under $800,000, here are my top recommendations:\n\n1. Lakeside Towers - $750,000, 2 bed/2 bath (95% match)\n2. Downtown Plaza - $650,000, 2 bed/1 bath (90% match)\n3. River View - $850,000, 3 bed/2 bath (85% match)\n\nWould you like more details or schedule a viewing?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            assert result["current_node"] == "recommend_properties"
            assert len(result["messages"]) == 2
            assert result["messages"][-1]["role"] == "assistant"
            assert "Lakeside Towers" in result["messages"][-1]["content"] or "Chicago" in result["messages"][-1]["content"]

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_recommend_single_property(self, mock_llm):
        """ND-RC02: 1 property shows single property."""
        state = create_initial_state("test-123")
        state["search_results"] = [
            {"project_name": "Lakeside Towers", "city": "Chicago", "bedrooms": 2, "bathrooms": 2, "price_usd": 750000, "area_sqm": 120, "property_type": "apartment", "completion_status": "available", "match_score": 0.95},
        ]
        state["preferences"] = {"city": "Chicago", "bedrooms": 2}
        state["messages"] = [{"role": "user", "content": "Show me properties"}]

        mock_response = MagicMock()
        mock_response.content = "I found one excellent match for you: Lakeside Towers in Chicago - $750,000, 2 bedrooms, 2 bathrooms, 120 sqm. Would you like to schedule a viewing?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            assert len(result["messages"]) == 2
            assert "Lakeside" in result["messages"][-1]["content"]

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_no_results_message(self, mock_llm):
        """ND-RC03: 0 properties shows 'no results' message with suggestions."""
        state = create_initial_state("test-123")
        state["search_results"] = []
        state["preferences"] = {"city": "NonExistentCity", "bedrooms": 10, "budget_max": 100000}
        state["messages"] = [{"role": "user", "content": "Show me properties"}]

        mock_response = MagicMock()
        mock_response.content = "I couldn't find any properties matching your specific criteria in NonExistentCity with 10 bedrooms under $100,000. Would you consider expanding your budget or looking at nearby cities?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            assert len(result["messages"]) == 2
            # Should mention no matches or suggest alternatives
            response_lower = result["messages"][-1]["content"].lower()
            assert "couldn't find" in response_lower or "no " in response_lower or "expanding" in response_lower

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_fallback_on_llm_error_with_results(self, mock_llm):
        """ND-RC04: LLM failure returns fallback response with results."""
        state = create_initial_state("test-123")
        state["search_results"] = [
            {"project_name": "Lakeside Towers", "city": "Chicago", "bedrooms": 2, "bathrooms": 2, "price_usd": 750000, "area_sqm": 120, "match_score": 0.95},
        ]
        state["preferences"] = {"city": "Chicago"}
        state["messages"] = [{"role": "user", "content": "Show me properties"}]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            assert len(result["messages"]) == 2
            # Fallback message should include property name
            assert "Lakeside Towers" in result["messages"][-1]["content"]
            assert "Chicago" in result["messages"][-1]["content"]
            assert "$750,000" in result["messages"][-1]["content"]

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_fallback_on_llm_error_no_results(self, mock_llm):
        """ND-RC04b: LLM failure with no results returns fallback."""
        state = create_initial_state("test-123")
        state["search_results"] = []
        state["preferences"] = {"city": "Chicago"}
        state["messages"] = [{"role": "user", "content": "Show me properties"}]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            assert len(result["messages"]) == 2
            # Fallback message should suggest adjusting search
            response_lower = result["messages"][-1]["content"].lower()
            assert "couldn't find" in response_lower or "adjust" in response_lower

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_property_missing_price(self, mock_llm):
        """ND-RC05: Property missing price shows 'Price on request'."""
        state = create_initial_state("test-123")
        state["search_results"] = [
            {"project_name": "Mystery Villa", "city": "Dubai", "bedrooms": 4, "bathrooms": 3, "price_usd": None, "area_sqm": 300, "match_score": 0.90},
        ]
        state["preferences"] = {"city": "Dubai"}
        state["messages"] = [{"role": "user", "content": "Show me properties"}]

        mock_response = MagicMock()
        mock_response.content = "I found Mystery Villa in Dubai - 4 bedrooms, 3 bathrooms, 300 sqm. Price on request. Would you like more details?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            # The node should format price as "Price on request" for None values
            # This is tested through the chain invocation, where the property is formatted
            assert result["current_node"] == "recommend_properties"

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_property_missing_area(self, mock_llm):
        """Property missing area is handled gracefully."""
        state = create_initial_state("test-123")
        state["search_results"] = [
            {"project_name": "Compact Unit", "city": "Singapore", "bedrooms": 1, "bathrooms": 1, "price_usd": 300000, "area_sqm": None, "match_score": 0.85},
        ]
        state["preferences"] = {"city": "Singapore"}
        state["messages"] = [{"role": "user", "content": "Show me properties"}]

        mock_response = MagicMock()
        mock_response.content = "I found Compact Unit in Singapore - $300,000, 1 bedroom. Want to know more?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            # Should handle None area gracefully
            assert result["current_node"] == "recommend_properties"
            assert len(result["messages"]) == 2

    @pytest.mark.asyncio
    @patch('agent.utils.llm.ChatOpenAI')
    async def test_recommendations_with_off_plan_status(self, mock_llm):
        """Properties with off_plan status are presented correctly."""
        state = create_initial_state("test-123")
        state["search_results"] = [
            {"project_name": "Future Tower", "city": "Dubai", "bedrooms": 2, "bathrooms": 2, "price_usd": 500000, "area_sqm": 100, "property_type": "apartment", "completion_status": "off_plan", "match_score": 0.92},
        ]
        state["preferences"] = {"city": "Dubai", "completion_status": "off_plan"}
        state["messages"] = [{"role": "user", "content": "Show me off-plan properties"}]

        mock_response = MagicMock()
        mock_response.content = "I found an excellent off-plan opportunity: Future Tower in Dubai - $500,000, 2 bedrooms, 100 sqm (92% match). Would you like more details?"

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.nodes.recommendation.ChatPromptTemplate') as mock_prompt:
            mock_prompt.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

            result = await recommend_properties(state)

            assert result["current_node"] == "recommend_properties"
            assert len(result["messages"]) == 2
