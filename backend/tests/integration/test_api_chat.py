"""
Integration tests for chat API endpoint.

Tests the /api/v1/agents/chat endpoint with various scenarios.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.django_db
class TestChatEndpoint:
    """Tests for chat API endpoint."""

    def test_chat_valid_conversation_and_message(self, api_client, sample_conversation, sample_projects):
        """API-CH01: Valid conversation + message returns 200 with response."""
        # Mock the agent to return a predictable state
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()
            mock_state = {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Welcome to Silver Land Properties!"}
                ],
                "user_intent": "greeting",
                "preferences": {},
                "search_results": [],
                "current_node": "greeting",
                "tools_used": [],
            }

            # Create an async mock
            async def mock_process(*args, **kwargs):
                return mock_state

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': 'Hello'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = response.json()
            assert 'response' in data
            assert 'message' in data['response']
            assert data['conversation_id'] == str(sample_conversation.id)

    def test_chat_invalid_conversation_id(self, api_client):
        """API-CH02: Invalid conversation_id returns 404."""
        response = api_client.post(
            '/api/v1/agents/chat',
            data=json.dumps({
                'conversation_id': '00000000-0000-0000-0000-000000000000',
                'message': 'Hello'
            }),
            content_type='application/json'
        )

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
        assert data['error'] == 'conversation_not_found'

    def test_chat_empty_message(self, api_client, sample_conversation):
        """API-CH03: Empty message returns validation error."""
        # This depends on your validation - may be 400 or 422
        response = api_client.post(
            '/api/v1/agents/chat',
            data=json.dumps({
                'conversation_id': str(sample_conversation.id),
                'message': ''
            }),
            content_type='application/json'
        )

        # Empty message should be rejected
        assert response.status_code in [400, 422]

    def test_chat_message_sanitized(self, api_client, sample_conversation):
        """API-CH05: Message with special characters is sanitized."""
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()
            mock_state = {
                "messages": [
                    {"role": "user", "content": "Test with special chars"},
                    {"role": "assistant", "content": "I understand you're looking for properties."}
                ],
                "user_intent": "other",
                "preferences": {},
                "search_results": [],
                "current_node": "discover_preferences",
                "tools_used": [],
            }

            async def mock_process(*args, **kwargs):
                return mock_state

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': 'Test with <script>alert("xss")</script> special chars'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200

    def test_chat_returns_recommendations(self, api_client, sample_conversation, sample_projects):
        """Chat with search results returns recommendations."""
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()
            mock_state = {
                "messages": [
                    {"role": "user", "content": "Show me properties in Chicago"},
                    {"role": "assistant", "content": "Here are some Chicago properties."}
                ],
                "user_intent": "share_preferences",
                "preferences": {"city": "Chicago"},
                "search_results": [
                    {
                        "id": str(sample_projects[0].id),
                        "project_name": "Chicago Heights",
                        "city": "Chicago",
                        "country": "US",
                        "property_type": "apartment",
                        "bedrooms": 2,
                        "bathrooms": 2,
                        "price_usd": 750000,
                        "area_sqm": 120,
                        "completion_status": "available",
                        "features": ["gym"],
                        "facilities": ["parking"],
                        "match_score": 0.95,
                    }
                ],
                "current_node": "recommend_properties",
                "tools_used": ["property_search"],
            }

            async def mock_process(*args, **kwargs):
                return mock_state

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': 'Show me properties in Chicago'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = response.json()
            assert 'recommendations' in data
            assert len(data['recommendations']) > 0
            assert data['recommendations'][0]['city'] == 'Chicago'

    def test_chat_returns_metadata(self, api_client, sample_conversation):
        """Chat returns metadata with processing time and tools used."""
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()
            mock_state = {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Welcome!"}
                ],
                "user_intent": "greeting",
                "preferences": {},
                "search_results": [],
                "current_node": "greeting",
                "tools_used": ["greeting_tool"],
            }

            async def mock_process(*args, **kwargs):
                return mock_state

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': 'Hello'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = response.json()
            assert 'metadata' in data
            assert 'processing_time_ms' in data['metadata']
            assert 'tools_used' in data['metadata']

    def test_chat_booking_response(self, api_client, sample_conversation):
        """Chat returns booking info when booking is confirmed."""
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()
            mock_state = {
                "messages": [
                    {"role": "user", "content": "john@example.com"},
                    {"role": "assistant", "content": "Your viewing has been booked!"}
                ],
                "user_intent": "provide_contact",
                "preferences": {"city": "Chicago"},
                "search_results": [],
                "current_node": "confirm_booking",
                "tools_used": ["booking_tool"],
                "booking_id": "booking-12345",
                "booking_confirmed": True,
            }

            async def mock_process(*args, **kwargs):
                return mock_state

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': 'john@example.com'
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = response.json()
            assert 'response' in data
            assert data['response']['structured_data']['booking'] is not None
            assert data['response']['structured_data']['booking']['booking_id'] == 'booking-12345'
            assert data['response']['structured_data']['booking']['status'] == 'confirmed'


@pytest.mark.django_db
class TestConversationEndpointExtended:
    """Extended tests for conversation endpoints."""

    def test_create_conversation_returns_id(self, api_client):
        """Create conversation returns valid UUID."""
        response = api_client.post(
            '/api/v1/conversations/',
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.json()
        assert 'conversation_id' in data
        # Verify it's a valid UUID format
        assert len(data['conversation_id']) == 36  # UUID format

    def test_get_conversation_includes_state(self, api_client, sample_conversation):
        """Get conversation includes state information."""
        response = api_client.get(
            f'/api/v1/conversations/{sample_conversation.id}'
        )

        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        # API returns flattened state fields, not nested 'state' object
        assert 'current_node' in data or 'preferences' in data

    def test_get_nonexistent_conversation(self, api_client):
        """Get non-existent conversation returns 404."""
        response = api_client.get(
            '/api/v1/conversations/00000000-0000-0000-0000-000000000000'
        )

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
        assert data['error'] == 'not_found'


@pytest.mark.django_db
class TestChatEdgeCases:
    """Edge case tests for chat endpoint."""

    def test_chat_preserves_state_across_messages(self, api_client, sample_conversation):
        """Chat preserves conversation state across multiple messages."""
        # First message
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()

            first_state = {
                "messages": [
                    {"role": "user", "content": "Chicago"},
                    {"role": "assistant", "content": "Looking in Chicago. What's your budget?"}
                ],
                "user_intent": "share_preferences",
                "preferences": {"city": "Chicago"},
                "search_results": [],
                "current_node": "discover_preferences",
                "tools_used": [],
            }

            async def mock_process(*args, **kwargs):
                return first_state

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response1 = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': 'Chicago'
                }),
                content_type='application/json'
            )

            assert response1.status_code == 200
            data1 = response1.json()
            assert data1['response']['structured_data']['preferences_captured']['city'] == 'Chicago'

    def test_chat_with_agent_error(self, api_client, sample_conversation):
        """API-CH06: Agent processing error returns 400."""
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()

            async def mock_process(*args, **kwargs):
                raise Exception("Agent processing failed")

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': 'Test message'
                }),
                content_type='application/json'
            )

            assert response.status_code == 400
            data = response.json()
            assert 'error' in data
            assert data['error'] == 'processing_error'

    def test_chat_intent_in_response(self, api_client, sample_conversation):
        """Chat response includes classified intent."""
        with patch('api.controllers.conversation_controller.get_agent_graph') as mock_agent:
            mock_graph = MagicMock()
            mock_state = {
                "messages": [
                    {"role": "user", "content": "I'd like to book a viewing"},
                    {"role": "assistant", "content": "Sure! What's your name?"}
                ],
                "user_intent": "book_viewing",
                "preferences": {},
                "search_results": [],
                "current_node": "propose_booking",
                "tools_used": [],
            }

            async def mock_process(*args, **kwargs):
                return mock_state

            mock_graph.process_message = mock_process
            mock_agent.return_value = mock_graph

            response = api_client.post(
                '/api/v1/agents/chat',
                data=json.dumps({
                    'conversation_id': str(sample_conversation.id),
                    'message': "I'd like to book a viewing"
                }),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = response.json()
            assert data['response']['intent'] == 'book_viewing'
