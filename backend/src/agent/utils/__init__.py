"""
Agent utilities for caching and LLM management.
"""
from .cache import (
    get_cached_intent,
    set_intent_cache,
    get_cached_property_search,
    set_property_search_cache,
    get_cached_web_search,
    set_web_search_cache,
    clear_all_cache,
    get_cache_stats,
)
from .llm import (
    get_llm,
    get_classifier_llm,
    get_conversational_llm,
    clear_llm_cache,
)

__all__ = [
    # Cache functions
    "get_cached_intent",
    "set_intent_cache",
    "get_cached_property_search",
    "set_property_search_cache",
    "get_cached_web_search",
    "set_web_search_cache",
    "clear_all_cache",
    "get_cache_stats",
    # LLM functions
    "get_llm",
    "get_classifier_llm",
    "get_conversational_llm",
    "clear_llm_cache",
]
