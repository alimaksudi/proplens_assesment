"""
Conversation state definition for LangGraph.

Defines the TypedDict used throughout the conversation flow
to maintain state between nodes.
"""

from typing import TypedDict, List, Dict, Optional, Literal, Any
from datetime import datetime


class Message(TypedDict):
    """Individual message in conversation."""
    role: Literal["user", "assistant", "system"]
    content: str


class Preferences(TypedDict, total=False):
    """User preferences extracted from conversation."""
    city: Optional[str]
    country: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    budget_min: Optional[float]
    budget_max: Optional[float]
    property_type: Optional[str]
    completion_status: Optional[str]
    features: Optional[List[str]]


class LeadData(TypedDict, total=False):
    """Lead contact information."""
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]


class PropertyResult(TypedDict):
    """Property search result."""
    id: int
    project_name: str
    city: str
    country: str
    property_type: Optional[str]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    price_usd: Optional[float]
    area_sqm: Optional[float]
    completion_status: Optional[str]
    features: List[str]
    facilities: List[str]
    description: Optional[str]
    match_score: Optional[float]


class ConversationState(TypedDict):
    """
    Complete state object for LangGraph conversation flow.

    This state is passed through each node and updated as the
    conversation progresses. It persists between API calls.
    """

    # Conversation metadata
    conversation_id: str
    current_node: str

    # Message history
    messages: List[Message]

    # User preferences
    preferences: Preferences
    preferences_complete: bool

    # Search results
    search_results: List[PropertyResult]
    recommended_projects: List[int]

    # Lead information (progressive capture)
    lead_data: LeadData
    lead_captured: bool
    lead_id: Optional[int]

    # Booking information
    selected_project_id: Optional[int]
    booking_id: Optional[int]
    booking_confirmed: bool

    # Intent tracking
    user_intent: Optional[Literal[
        "greeting",
        "share_preferences",
        "ask_question",
        "request_recommendations",
        "express_interest",
        "book_viewing",
        "provide_contact",
        "clarify",
        "goodbye",
        "other"
    ]]

    # Error handling
    error_message: Optional[str]
    retry_count: int

    # Tools tracking
    tools_used: List[str]

    # Timestamps
    created_at: str
    last_updated: str


def create_initial_state(conversation_id: str) -> ConversationState:
    """Create a new conversation state with defaults."""
    now = datetime.utcnow().isoformat()

    return {
        "conversation_id": conversation_id,
        "current_node": "greeting",
        "messages": [],
        "preferences": {},
        "preferences_complete": False,
        "search_results": [],
        "recommended_projects": [],
        "lead_data": {},
        "lead_captured": False,
        "lead_id": None,
        "selected_project_id": None,
        "booking_id": None,
        "booking_confirmed": False,
        "user_intent": None,
        "error_message": None,
        "retry_count": 0,
        "tools_used": [],
        "created_at": now,
        "last_updated": now,
    }


def update_state_timestamp(state: ConversationState) -> ConversationState:
    """Update the last_updated timestamp in state."""
    state["last_updated"] = datetime.utcnow().isoformat()
    return state
