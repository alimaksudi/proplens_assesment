"""
Agent configuration module.

Centralizes all agent-related configuration including:
- LLM settings (model, temperature, max_tokens)
- Intent categories
- Fallback messages
"""
import os
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """Configuration for LLM instances."""
    model: str = field(default_factory=lambda: os.getenv('OPENAI_MODEL', 'gpt-4o-mini'))
    temperature_classification: float = 0.0  # For deterministic tasks
    temperature_conversation: float = 0.7    # For creative responses
    temperature_extraction: float = 0.0      # For data extraction
    max_tokens: int = field(default_factory=lambda: int(os.getenv('OPENAI_MAX_TOKENS', '2048')))


@dataclass
class CacheConfig:
    """Configuration for caching TTLs."""
    intent_ttl: int = 300           # 5 minutes
    property_search_ttl: int = 600  # 10 minutes
    web_search_ttl: int = 1800      # 30 minutes


# =============================================================================
# Intent Categories
# =============================================================================

INTENT_CATEGORIES: List[str] = [
    "greeting",
    "share_preferences",
    "ask_question",
    "request_recommendations",
    "express_interest",
    "book_viewing",
    "provide_contact",
    "clarify",
    "goodbye",
    "other",
]

INTENT_DESCRIPTIONS: Dict[str, str] = {
    "greeting": "User is saying hello or starting conversation",
    "share_preferences": "User is sharing/updating property preferences (location, budget, bedrooms, etc.)",
    "ask_question": "User is asking a question about a property or general inquiry",
    "request_recommendations": "User wants to see property results with current criteria",
    "express_interest": "User is showing interest in a specific property already shown",
    "book_viewing": "User wants to schedule a property viewing",
    "provide_contact": "User is providing contact information (name, email, phone)",
    "clarify": "User is clarifying or correcting previous information",
    "goodbye": "User is ending the conversation",
    "other": "None of the above",
}


# =============================================================================
# Fallback Messages
# =============================================================================

FALLBACK_MESSAGES: Dict[str, str] = {
    # Greeting fallbacks
    "greeting_welcome": (
        "Welcome to Silver Land Properties! I'm your personal property assistant. "
        "I can help you find your dream property, schedule viewings, and answer any questions. "
        "What type of property are you looking for today?"
    ),
    "greeting_error": (
        "Welcome to Silver Land Properties! I'm here to help you find your perfect property. "
        "What are you looking for today?"
    ),

    # Goodbye messages
    "goodbye_after_booking": (
        "You're all set! We'll be in touch soon about your viewing. Have a wonderful day!"
    ),
    "goodbye_general": (
        "Thank you for exploring properties with Silver Land! "
        "Feel free to return whenever you're ready. Have a great day!"
    ),

    # Error fallbacks
    "recommendation_error": (
        "I found some great properties that might interest you. "
        "Would you like more details about any of them?"
    ),
    "booking_error": (
        "I'd be happy to help arrange a viewing for you. "
        "Could you please share your name and email address?"
    ),
    "qa_error": (
        "I apologize, but I'm having trouble answering that question right now. "
        "Could you please rephrase it or ask something else?"
    ),

    # No results
    "no_properties_found": (
        "I couldn't find properties matching your exact criteria. "
        "Would you like to adjust your preferences or see similar options?"
    ),
    "no_search_results": (
        "I couldn't find information about that. "
        "Could you provide more details or ask a different question?"
    ),
}


# =============================================================================
# Property Types and Options
# =============================================================================

PROPERTY_TYPES: List[str] = [
    "apartment",
    "villa",
    "townhouse",
    "penthouse",
    "studio",
    "duplex",
]

COMPLETION_STATUSES: List[str] = [
    "ready",
    "off-plan",
    "under_construction",
]


# =============================================================================
# Default Configurations
# =============================================================================

# Default LLM configuration instance
llm_config = LLMConfig()

# Default cache configuration instance
cache_config = CacheConfig()


def get_llm_config() -> LLMConfig:
    """Get the current LLM configuration."""
    return llm_config


def get_cache_config() -> CacheConfig:
    """Get the current cache configuration."""
    return cache_config


def get_intent_categories() -> List[str]:
    """Get the list of valid intent categories."""
    return INTENT_CATEGORIES.copy()


def get_fallback_message(key: str, default: str = "") -> str:
    """
    Get a fallback message by key.

    Args:
        key: The message key (e.g., 'greeting_welcome', 'goodbye_general')
        default: Default message if key not found

    Returns:
        The fallback message string
    """
    return FALLBACK_MESSAGES.get(key, default)
