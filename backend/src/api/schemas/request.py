"""
Request schemas for API endpoints.
"""

from ninja import Schema
from typing import Optional


class CreateConversationRequest(Schema):
    """Request schema for creating a new conversation."""
    pass


class ChatRequest(Schema):
    """Request schema for sending a message to the agent."""
    conversation_id: str
    message: str
