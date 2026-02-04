"""
Integration tests for API endpoints.
"""

import pytest
import json


@pytest.mark.django_db
class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, api_client):
        """Test health check returns healthy status."""
        response = api_client.get('/api/v1/health/')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert 'version' in data


@pytest.mark.django_db
class TestConversationEndpoints:
    """Tests for conversation management endpoints."""

    def test_create_conversation(self, api_client):
        """Test creating a new conversation."""
        response = api_client.post(
            '/api/v1/conversations/',
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.json()
        assert 'conversation_id' in data
        assert 'created_at' in data

    def test_get_conversation(self, api_client, sample_conversation):
        """Test getting conversation details."""
        response = api_client.get(
            f'/api/v1/conversations/{sample_conversation.id}'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == str(sample_conversation.id)

    def test_get_nonexistent_conversation(self, api_client):
        """Test getting non-existent conversation returns 404."""
        response = api_client.get(
            '/api/v1/conversations/00000000-0000-0000-0000-000000000000'
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestChatEndpoint:
    """Tests for chat endpoint."""

    def test_chat_nonexistent_conversation(self, api_client):
        """Test chat with non-existent conversation returns 404."""
        response = api_client.post(
            '/api/v1/agents/chat',
            data=json.dumps({
                'conversation_id': '00000000-0000-0000-0000-000000000000',
                'message': 'Hello'
            }),
            content_type='application/json'
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestPropertySearchIntegration:
    """Integration tests for property search functionality."""

    def test_search_properties_by_city(self, api_client, sample_projects, sample_conversation):
        """Test searching properties returns results."""
        from domain.models import Project

        # Verify we have Chicago properties
        chicago_projects = Project.objects.filter(city__icontains="Chicago")
        assert chicago_projects.count() >= 2


@pytest.mark.django_db
class TestBookingIntegration:
    """Integration tests for booking functionality."""

    def test_booking_creation(self, sample_booking):
        """Test booking is created correctly."""
        assert sample_booking.id is not None
        assert sample_booking.lead is not None
        assert sample_booking.project is not None
        assert sample_booking.status == "pending"

    def test_booking_updates_status(self, sample_booking):
        """Test booking status can be updated."""
        sample_booking.status = "confirmed"
        sample_booking.save()
        sample_booking.refresh_from_db()

        assert sample_booking.status == "confirmed"
