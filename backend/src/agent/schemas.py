"""
Pydantic schemas for input validation in the agent.

Provides type safety and validation for user inputs,
state mutations, and API requests.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, EmailStr
from decimal import Decimal
import re


class MessageInput(BaseModel):
    """Validates user message input."""
    content: str = Field(..., min_length=1, max_length=5000)

    @field_validator('content')
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Remove null bytes and excessive whitespace."""
        # Remove null bytes
        v = v.replace('\x00', '')
        # Normalize whitespace
        v = ' '.join(v.split())
        return v.strip()


class PreferencesInput(BaseModel):
    """Validates user preferences."""
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=2)
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[int] = Field(None, ge=0, le=20)
    budget_min: Optional[float] = Field(None, ge=0, le=1_000_000_000)
    budget_max: Optional[float] = Field(None, ge=0, le=1_000_000_000)
    property_type: Optional[Literal['apartment', 'villa', 'house', 'condo']] = None
    completion_status: Optional[Literal['available', 'off_plan', 'under_construction', 'completed']] = None
    features: Optional[List[str]] = Field(default_factory=list, max_length=20)

    @field_validator('city', 'country')
    @classmethod
    def sanitize_location(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        # Remove special characters except spaces and hyphens
        v = re.sub(r'[^\w\s\-]', '', v)
        return v.strip()[:100]

    @field_validator('budget_min', 'budget_max')
    @classmethod
    def validate_budget(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            return 0
        if v is not None and v > 1_000_000_000:
            return 1_000_000_000
        return v


class LeadDataInput(BaseModel):
    """Validates lead contact information."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)

    @field_validator('first_name', 'last_name')
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        # Remove everything except letters, spaces, hyphens, apostrophes
        v = re.sub(r"[^\w\s\-']", '', v)
        return v.strip()[:100]

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        # Basic email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v.strip()):
            return None  # Return None for invalid emails instead of raising
        return v.strip().lower()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        # Keep only digits and common phone characters
        v = re.sub(r'[^\d\+\-\(\)\s]', '', v)
        # Must have at least 7 digits
        digits = re.sub(r'\D', '', v)
        if len(digits) < 7:
            return None
        return v.strip()[:50]


class ChatRequest(BaseModel):
    """Validates incoming chat API requests."""
    conversation_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=5000)

    @field_validator('conversation_id')
    @classmethod
    def validate_conversation_id(cls, v: str) -> str:
        # Allow UUIDs and alphanumeric IDs
        if not re.match(r'^[a-zA-Z0-9\-_]+$', v):
            raise ValueError('Invalid conversation ID format')
        return v

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        # Remove null bytes
        v = v.replace('\x00', '')
        # Normalize whitespace
        v = ' '.join(v.split())
        return v.strip()


def validate_preferences(data: dict) -> dict:
    """
    Validate and sanitize preferences dict.
    Returns cleaned preferences or empty dict on validation failure.
    """
    try:
        validated = PreferencesInput(**data)
        return validated.model_dump(exclude_none=True)
    except Exception:
        return {}


def validate_lead_data(data: dict) -> dict:
    """
    Validate and sanitize lead data dict.
    Returns cleaned lead data or empty dict on validation failure.
    """
    try:
        validated = LeadDataInput(**data)
        return validated.model_dump(exclude_none=True)
    except Exception:
        return {}


def validate_message(content: str) -> str:
    """
    Validate and sanitize a message string.
    Returns cleaned message or raises ValueError.
    """
    validated = MessageInput(content=content)
    return validated.content


def validate_chat_request(conversation_id: str, message: str) -> ChatRequest:
    """
    Validate a chat API request.
    Returns ChatRequest or raises ValueError.
    """
    return ChatRequest(conversation_id=conversation_id, message=message)
