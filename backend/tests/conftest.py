"""
Pytest configuration and fixtures.
"""

import os
import sys
import pytest
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from domain.models import Project, Lead, Booking, Conversation


@pytest.fixture
def sample_project(db):
    """Create a sample project for testing."""
    return Project.objects.create(
        project_name="Test Property Chicago",
        developer_name="Test Developer",
        city="Chicago",
        country="US",
        property_type="apartment",
        bedrooms=2,
        bathrooms=2,
        price_usd=Decimal("850000.00"),
        area_sqm=Decimal("150.00"),
        completion_status="available",
        features=["gym", "pool"],
        facilities=["parking", "security"],
        description="A beautiful test property in Chicago.",
        is_valid=True,
    )


@pytest.fixture
def sample_projects(db):
    """Create multiple sample projects for testing."""
    projects = []

    # Chicago apartment
    projects.append(Project.objects.create(
        project_name="Chicago Heights",
        developer_name="Urban Living",
        city="Chicago",
        country="US",
        property_type="apartment",
        bedrooms=2,
        bathrooms=2,
        price_usd=Decimal("750000.00"),
        area_sqm=Decimal("120.00"),
        completion_status="available",
        is_valid=True,
    ))

    # Chicago villa
    projects.append(Project.objects.create(
        project_name="Chicago Lake Villa",
        developer_name="Luxury Homes",
        city="Chicago",
        country="US",
        property_type="villa",
        bedrooms=4,
        bathrooms=3,
        price_usd=Decimal("1500000.00"),
        area_sqm=Decimal("350.00"),
        completion_status="available",
        is_valid=True,
    ))

    # Singapore apartment
    projects.append(Project.objects.create(
        project_name="Singapore Marina",
        developer_name="Asia Developers",
        city="Singapore",
        country="SG",
        property_type="apartment",
        bedrooms=3,
        bathrooms=2,
        price_usd=Decimal("2000000.00"),
        area_sqm=Decimal("200.00"),
        completion_status="off_plan",
        is_valid=True,
    ))

    return projects


@pytest.fixture
def sample_conversation(db):
    """Create a sample conversation for testing."""
    from agent.state import create_initial_state
    import uuid

    conv_id = str(uuid.uuid4())
    conversation = Conversation.objects.create(
        state=create_initial_state(conv_id)
    )
    conversation.state['conversation_id'] = str(conversation.id)
    conversation.save()
    return conversation


@pytest.fixture
def sample_lead(db, sample_conversation):
    """Create a sample lead for testing."""
    return Lead.objects.create(
        conversation_id=sample_conversation.id,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1234567890",
        preferences={
            "city": "Chicago",
            "bedrooms": 2,
            "budget_max": 1000000,
        },
    )


@pytest.fixture
def sample_booking(db, sample_lead, sample_project, sample_conversation):
    """Create a sample booking for testing."""
    return Booking.objects.create(
        lead=sample_lead,
        project=sample_project,
        conversation_id=sample_conversation.id,
        status="pending",
        notes="Test booking",
    )


@pytest.fixture
def api_client():
    """Create Django test client."""
    from django.test import Client
    return Client()
