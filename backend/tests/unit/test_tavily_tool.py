"""
Unit tests for TavilySearchTool.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from agent.tools.tavily_search_tool import (
    TavilySearchTool,
    get_tavily_tool,
    should_search_web,
    needs_external_info,
    is_broad_recommendation_query,
    EXTERNAL_INFO_KEYWORDS,
    BROAD_SEARCH_KEYWORDS,
)


class TestTavilySearchTool:
    """Tests for TavilySearchTool class."""

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('agent.tools.tavily_search_tool.TAVILY_AVAILABLE', True):
                tool = TavilySearchTool()
                assert tool.api_key is None
                assert tool.client is None

    def test_init_with_config_api_key(self):
        """Test initialization with API key in config."""
        with patch('agent.tools.tavily_search_tool.TAVILY_AVAILABLE', True):
            with patch('agent.tools.tavily_search_tool.TavilyClient') as mock_client:
                tool = TavilySearchTool(config={'api_key': 'test-key'})
                assert tool.api_key == 'test-key'
                mock_client.assert_called_once_with(api_key='test-key')

    def test_is_available_with_client(self):
        """Test is_available returns True when client exists."""
        tool = TavilySearchTool()
        tool.client = Mock()
        assert tool.is_available() is True

    def test_is_available_without_client(self):
        """Test is_available returns False when no client."""
        tool = TavilySearchTool()
        tool.client = None
        assert tool.is_available() is False

    def test_build_search_query_basic(self):
        """Test query building with just a question."""
        tool = TavilySearchTool()
        query = tool._build_search_query("What are the schools nearby?")
        assert query == "What are the schools nearby?"

    def test_build_search_query_with_location(self):
        """Test query building with location context."""
        tool = TavilySearchTool()
        query = tool._build_search_query(
            "What are the schools nearby?",
            location="Chicago"
        )
        assert query == "Chicago What are the schools nearby?"

    def test_build_search_query_with_project_name(self):
        """Test query building with project name context."""
        tool = TavilySearchTool()
        query = tool._build_search_query(
            "What are the schools nearby?",
            project_name="Lakeside Towers"
        )
        assert query == "Lakeside Towers What are the schools nearby?"

    def test_build_search_query_with_all_context(self):
        """Test query building with all context."""
        tool = TavilySearchTool()
        query = tool._build_search_query(
            "What are the schools nearby?",
            project_name="Lakeside Towers",
            location="Chicago"
        )
        assert query == "Chicago Lakeside Towers What are the schools nearby?"

    def test_build_search_query_project_already_in_query(self):
        """Test that project name is not duplicated if already in query."""
        tool = TavilySearchTool()
        query = tool._build_search_query(
            "What are the schools near Lakeside Towers?",
            project_name="Lakeside Towers"
        )
        assert query == "What are the schools near Lakeside Towers?"

    def test_format_results_success(self):
        """Test formatting of successful API response."""
        tool = TavilySearchTool()
        response = {
            "answer": "There are several schools nearby.",
            "query": "schools near project",
            "results": [
                {
                    "title": "Lincoln Elementary",
                    "content": "A great public school",
                    "url": "https://example.com/school1",
                    "score": 0.95
                },
                {
                    "title": "Washington High",
                    "content": "Top rated high school",
                    "url": "https://example.com/school2",
                    "score": 0.90
                }
            ]
        }

        formatted = tool._format_results(response)

        assert formatted["success"] is True
        assert formatted["answer"] == "There are several schools nearby."
        assert len(formatted["results"]) == 2
        assert formatted["results"][0]["title"] == "Lincoln Elementary"
        assert formatted["results"][1]["title"] == "Washington High"

    @pytest.mark.asyncio
    async def test_search_without_client(self):
        """Test search returns error when client not available."""
        tool = TavilySearchTool()
        tool.client = None

        result = await tool.search("What schools are nearby?")

        assert result["success"] is False
        assert result["error"] == "Web search not configured"
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_search_success(self):
        """Test successful search."""
        tool = TavilySearchTool()
        mock_client = Mock()
        mock_client.search.return_value = {
            "answer": "Great schools in the area.",
            "query": "schools Chicago",
            "results": [
                {
                    "title": "Local School",
                    "content": "Description",
                    "url": "https://example.com",
                    "score": 0.9
                }
            ]
        }
        tool.client = mock_client

        result = await tool.search("What schools are nearby?", location="Chicago")

        assert result["success"] is True
        assert result["answer"] == "Great schools in the area."
        assert len(result["results"]) == 1

    @pytest.mark.asyncio
    async def test_search_handles_exception(self):
        """Test search handles API exceptions gracefully."""
        tool = TavilySearchTool()
        mock_client = Mock()
        mock_client.search.side_effect = Exception("API Error")
        tool.client = mock_client

        result = await tool.search("What schools are nearby?")

        assert result["success"] is False
        assert "API Error" in result["error"]


class TestKeywordDetection:
    """Tests for keyword detection functions."""

    @pytest.mark.parametrize("question,expected", [
        ("What schools are near this property?", True),
        ("Is there public transport nearby?", True),
        ("What's the neighborhood like?", True),
        ("Are there any hospitals close by?", True),
        ("What restaurants are in the area?", True),
        ("Tell me about the metro stations", True),
        ("Show me 2-bedroom apartments", False),
        ("What is the price?", False),
        ("How many bathrooms does it have?", False),
    ])
    def test_needs_external_info(self, question, expected):
        """Test detection of questions needing external info."""
        assert needs_external_info(question) == expected

    @pytest.mark.parametrize("question,expected", [
        ("Show me 2-bedroom apartments in Chicago", True),
        ("Find properties under $1 million", True),
        ("I'm looking for a villa with 3 bathrooms", True),
        ("What apartments are available?", True),
        ("What schools are nearby?", False),
        ("Tell me about the neighborhood", False),
        ("Is there a gym close by?", False),
    ])
    def test_is_broad_recommendation_query(self, question, expected):
        """Test detection of broad recommendation queries."""
        assert is_broad_recommendation_query(question) == expected

    @pytest.mark.parametrize("question,expected", [
        # Should trigger web search (external info, not broad)
        ("What schools are near Lakeside Towers?", True),
        ("Is there public transport close to this property?", True),
        ("What's the neighborhood like around here?", True),
        ("Are there any good restaurants nearby?", True),

        # Should NOT trigger web search (broad recommendation)
        ("Show me 2-bedroom apartments near schools", False),
        ("Find properties close to transport", False),
        ("I'm looking for a property in a good neighborhood", False),

        # Should NOT trigger web search (no external info needed)
        ("What is the price of this apartment?", False),
        ("How many bedrooms does it have?", False),
        ("Tell me more about the features", False),
    ])
    def test_should_search_web(self, question, expected):
        """Test combined logic for web search decision."""
        assert should_search_web(question) == expected


class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_tavily_tool_returns_same_instance(self):
        """Test that get_tavily_tool returns singleton."""
        # Reset singleton for test
        import agent.tools.tavily_search_tool as module
        module._tavily_instance = None

        tool1 = get_tavily_tool()
        tool2 = get_tavily_tool()

        assert tool1 is tool2

        # Clean up
        module._tavily_instance = None
