"""
Unit tests for domain models.
"""

import pytest
from decimal import Decimal
from domain.models import Project, Lead, Booking, Conversation


@pytest.mark.django_db
class TestProjectModel:
    """Tests for the Project model."""

    def test_create_project(self, sample_project):
        """Test creating a project."""
        assert sample_project.id is not None
        assert sample_project.project_name == "Test Property Chicago"
        assert sample_project.city == "Chicago"
        assert sample_project.bedrooms == 2

    def test_project_to_dict(self, sample_project):
        """Test project to_dict method."""
        data = sample_project.to_dict()

        assert data['id'] == sample_project.id
        assert data['project_name'] == "Test Property Chicago"
        assert data['price_usd'] == 850000.0
        assert data['bedrooms'] == 2

    def test_project_str(self, sample_project):
        """Test project string representation."""
        assert str(sample_project) == "Test Property Chicago - Chicago"

    def test_get_key_features(self, sample_project):
        """Test get_key_features method."""
        features = sample_project.get_key_features(limit=3)
        assert len(features) <= 3
        assert "gym" in features


@pytest.mark.django_db
class TestLeadModel:
    """Tests for the Lead model."""

    def test_create_lead(self, sample_lead):
        """Test creating a lead."""
        assert sample_lead.id is not None
        assert sample_lead.first_name == "John"
        assert sample_lead.email == "john.doe@example.com"

    def test_lead_full_name(self, sample_lead):
        """Test lead full_name property."""
        assert sample_lead.full_name == "John Doe"

    def test_lead_is_complete(self, sample_lead):
        """Test lead is_complete method."""
        assert sample_lead.is_complete() is True

    def test_lead_incomplete(self, db, sample_conversation):
        """Test incomplete lead."""
        lead = Lead.objects.create(
            conversation_id=sample_conversation.id,
            first_name="Jane",
        )
        assert lead.is_complete() is False

    def test_lead_to_dict(self, sample_lead):
        """Test lead to_dict method."""
        data = sample_lead.to_dict()

        assert data['first_name'] == "John"
        assert data['email'] == "john.doe@example.com"
        assert data['is_complete'] is True


@pytest.mark.django_db
class TestBookingModel:
    """Tests for the Booking model."""

    def test_create_booking(self, sample_booking):
        """Test creating a booking."""
        assert sample_booking.id is not None
        assert sample_booking.status == "pending"

    def test_booking_to_dict(self, sample_booking):
        """Test booking to_dict method."""
        data = sample_booking.to_dict()

        assert data['status'] == "pending"
        assert data['lead']['name'] == "John Doe"
        assert data['project']['name'] == "Test Property Chicago"


@pytest.mark.django_db
class TestConversationModel:
    """Tests for the Conversation model."""

    def test_create_conversation(self, sample_conversation):
        """Test creating a conversation."""
        assert sample_conversation.id is not None
        assert sample_conversation.state is not None

    def test_conversation_get_messages(self, sample_conversation):
        """Test get_messages method."""
        sample_conversation.state['messages'] = [
            {"role": "user", "content": "Hello"}
        ]
        sample_conversation.save()

        messages = sample_conversation.get_messages()
        assert len(messages) == 1
        assert messages[0]['content'] == "Hello"

    def test_conversation_get_preferences(self, sample_conversation):
        """Test get_preferences method."""
        sample_conversation.state['preferences'] = {"city": "Chicago"}
        sample_conversation.save()

        prefs = sample_conversation.get_preferences()
        assert prefs['city'] == "Chicago"
