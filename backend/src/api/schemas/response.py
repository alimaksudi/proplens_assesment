"""
Response schemas for API endpoints.
"""

from ninja import Schema
from typing import List, Dict, Optional, Any
from datetime import datetime


class PropertyRecommendation(Schema):
    """Schema for property recommendation in responses."""
    id: int
    project_name: str
    city: str
    country: str
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    price_usd: Optional[float] = None
    area_sqm: Optional[float] = None
    completion_status: Optional[str] = None
    key_features: List[str] = []
    match_score: Optional[float] = None
    description: Optional[str] = None


class StructuredData(Schema):
    """Structured data in chat response."""
    preferences_captured: Optional[Dict[str, Any]] = None
    next_questions: Optional[List[str]] = None
    booking: Optional[Dict[str, Any]] = None


class ResponseContent(Schema):
    """Content of the agent response."""
    message: str
    intent: Optional[str] = None
    structured_data: Optional[StructuredData] = None
    state: str


class Metadata(Schema):
    """Metadata about the response."""
    processing_time_ms: int
    tools_used: List[str] = []


class ChatResponse(Schema):
    """Response schema for chat endpoint."""
    conversation_id: str
    response: ResponseContent
    recommendations: List[PropertyRecommendation] = []
    metadata: Metadata


class ConversationResponse(Schema):
    """Response schema for conversation creation."""
    conversation_id: str
    created_at: datetime


class ErrorResponse(Schema):
    """Error response schema."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
