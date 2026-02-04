"""
Unit tests for the greeting node.

Tests the greet_user function that handles conversation initialization.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from agent.state import create_initial_state
from agent.nodes.greeting import greet_user


@pytest.mark.django_db
class TestGreetingNode:
    """Tests for greeting node functionality."""

    @pytest.mark.asyncio
    async def test_greeting_on_hello(self):
        """ND-GR01: First message 'Hello' generates greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Hello"}]

        mock_response = MagicMock()
        mock_response.content = "Welcome to Silver Land Properties! I'm your property assistant."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.utils.llm.ChatOpenAI'):
            with patch('agent.nodes.greeting.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await greet_user(state)

                assert result["current_node"] == "greeting"
                assert len(result["messages"]) == 2
                assert result["messages"][-1]["role"] == "assistant"
                assert "Welcome" in result["messages"][-1]["content"] or "property" in result["messages"][-1]["content"].lower()

    @pytest.mark.asyncio
    async def test_skip_greeting_on_looking_for(self):
        """ND-GR02: First message 'Looking for apartments' skips greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Looking for apartments in Dubai"}]

        result = await greet_user(state)

        # Should not add any assistant message
        assert len(result["messages"]) == 1
        assert result["current_node"] == "greeting"

    @pytest.mark.asyncio
    async def test_skip_greeting_on_need(self):
        """ND-GR03: First message 'I need a 2-bedroom' skips greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "I need a 2-bedroom apartment"}]

        result = await greet_user(state)

        # Should not add any assistant message
        assert len(result["messages"]) == 1
        assert result["current_node"] == "greeting"

    @pytest.mark.asyncio
    async def test_skip_greeting_when_assistant_messages_exist(self):
        """ND-GR04: Already has assistant messages - skip greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]

        result = await greet_user(state)

        # Should not add another assistant message
        assert len(result["messages"]) == 3
        assert result["current_node"] == "greeting"

    @pytest.mark.asyncio
    async def test_no_greeting_on_empty_messages(self):
        """ND-GR05: Empty message list returns state unchanged."""
        state = create_initial_state("test-123")
        state["messages"] = []

        result = await greet_user(state)

        assert len(result["messages"]) == 0
        assert result["current_node"] == "greeting"

    @pytest.mark.asyncio
    async def test_fallback_greeting_on_api_error(self):
        """ND-GR06: OpenAI API failure returns fallback greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Hi there"}]

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(side_effect=Exception("API Error"))

        with patch('agent.utils.llm.ChatOpenAI'):
            with patch('agent.nodes.greeting.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await greet_user(state)

                assert len(result["messages"]) == 2
                assert result["messages"][-1]["role"] == "assistant"
                # Fallback message should be the hardcoded one
                assert "Silver Land Properties" in result["messages"][-1]["content"]
                assert "I'm here to help" in result["messages"][-1]["content"]

    @pytest.mark.asyncio
    async def test_skip_greeting_on_show_me(self):
        """First message 'Show me apartments' skips greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Show me 2-bedroom apartments"}]

        result = await greet_user(state)

        # Should not add any assistant message
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_skip_greeting_on_find(self):
        """First message 'Find me a property' skips greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Find me a property in Chicago"}]

        result = await greet_user(state)

        # Should not add any assistant message
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_skip_greeting_on_want(self):
        """First message 'I want an apartment' skips greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "I want an apartment under $500k"}]

        result = await greet_user(state)

        # Should not add any assistant message
        assert len(result["messages"]) == 1

    @pytest.mark.asyncio
    async def test_greeting_on_good_morning(self):
        """First message 'Good morning' generates greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Good morning"}]

        mock_response = MagicMock()
        mock_response.content = "Good morning! Welcome to Silver Land Properties."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.utils.llm.ChatOpenAI'):
            with patch('agent.nodes.greeting.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await greet_user(state)

                assert len(result["messages"]) == 2
                assert result["messages"][-1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_greeting_on_hey(self):
        """First message 'Hey' generates greeting."""
        state = create_initial_state("test-123")
        state["messages"] = [{"role": "user", "content": "Hey"}]

        mock_response = MagicMock()
        mock_response.content = "Hey there! Welcome to Silver Land Properties."

        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        with patch('agent.utils.llm.ChatOpenAI'):
            with patch('agent.nodes.greeting.ChatPromptTemplate') as mock_prompt:
                mock_prompt.from_messages.return_value.__or__ = MagicMock(return_value=mock_chain)

                result = await greet_user(state)

                assert len(result["messages"]) == 2
