"""
Centralized prompt management for the conversational agent.

All prompts are defined here for easy maintenance, versioning, and updates.
"""
from .intent_classifier import INTENT_CLASSIFICATION_PROMPT
from .greeting import GREETING_SYSTEM_PROMPT, GREETING_USER_PROMPT
from .preference_discovery import PREFERENCE_EXTRACTION_PROMPT, PREFERENCE_RESPONSE_PROMPT
from .lead_capture import LEAD_EXTRACTION_PROMPT, LEAD_FOLLOWUP_PROMPT
from .question_answering import QA_PROMPT, QA_PROMPT_WITH_WEB_SEARCH
from .recommendation import RECOMMENDATION_PROMPT, NO_RESULTS_PROMPT
from .booking import BOOKING_PROPOSAL_PROMPT

__all__ = [
    # Intent classification
    "INTENT_CLASSIFICATION_PROMPT",
    # Greeting
    "GREETING_SYSTEM_PROMPT",
    "GREETING_USER_PROMPT",
    # Preference discovery
    "PREFERENCE_EXTRACTION_PROMPT",
    "PREFERENCE_RESPONSE_PROMPT",
    # Lead capture
    "LEAD_EXTRACTION_PROMPT",
    "LEAD_FOLLOWUP_PROMPT",
    # Question answering
    "QA_PROMPT",
    "QA_PROMPT_WITH_WEB_SEARCH",
    # Recommendation
    "RECOMMENDATION_PROMPT",
    "NO_RESULTS_PROMPT",
    # Booking
    "BOOKING_PROPOSAL_PROMPT",
]
