"""
Caching utilities for the conversational agent.

Provides functions to cache and retrieve:
- Intent classification results
- Property search results
- Web search results
"""
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_cache_key(prefix: str, **kwargs) -> str:
    """
    Generate a consistent cache key from arguments.

    Args:
        prefix: Cache key prefix (e.g., "intent", "property_search")
        **kwargs: Key-value pairs to include in the hash

    Returns:
        Cache key string in format "prefix:hash"
    """
    # Sort kwargs for consistent key generation
    key_data = json.dumps(kwargs, sort_keys=True, default=str)
    hash_value = hashlib.md5(key_data.encode()).hexdigest()[:16]
    return f"{prefix}:{hash_value}"


# =============================================================================
# Intent Classification Caching
# =============================================================================

def get_cached_intent(message: str) -> Optional[str]:
    """
    Get cached intent for a message.

    Args:
        message: User message

    Returns:
        Cached intent string or None if not cached
    """
    cache_key = generate_cache_key("intent", message=message.lower().strip())
    result = cache.get(cache_key)
    if result:
        logger.debug(f"Cache HIT for intent: {message[:50]}...")
    return result


def set_intent_cache(message: str, intent: str) -> None:
    """
    Cache intent classification result.

    Args:
        message: User message
        intent: Classified intent
    """
    cache_key = generate_cache_key("intent", message=message.lower().strip())
    ttl = getattr(settings, 'CACHE_TTL_INTENT', 300)
    cache.set(cache_key, intent, ttl)
    logger.debug(f"Cached intent '{intent}' for: {message[:50]}...")


# =============================================================================
# Property Search Caching
# =============================================================================

def get_cached_property_search(preferences: Dict[str, Any]) -> Optional[List[Dict]]:
    """
    Get cached property search results.

    Args:
        preferences: Search preferences dictionary

    Returns:
        Cached search results list or None if not cached
    """
    # Only cache based on search-relevant preferences
    search_params = {
        k: v for k, v in preferences.items()
        if k in ['city', 'country', 'bedrooms', 'budget_min', 'budget_max', 'property_type']
        and v is not None
    }
    cache_key = generate_cache_key("property_search", **search_params)
    result = cache.get(cache_key)
    if result:
        logger.debug(f"Cache HIT for property search: {search_params}")
    return result


def set_property_search_cache(preferences: Dict[str, Any], results: List[Dict]) -> None:
    """
    Cache property search results.

    Args:
        preferences: Search preferences dictionary
        results: List of property results to cache
    """
    search_params = {
        k: v for k, v in preferences.items()
        if k in ['city', 'country', 'bedrooms', 'budget_min', 'budget_max', 'property_type']
        and v is not None
    }
    cache_key = generate_cache_key("property_search", **search_params)
    ttl = getattr(settings, 'CACHE_TTL_PROPERTY_SEARCH', 600)
    cache.set(cache_key, results, ttl)
    logger.debug(f"Cached {len(results)} property results for: {search_params}")


# =============================================================================
# Web Search Caching
# =============================================================================

def get_cached_web_search(query: str, location: Optional[str] = None) -> Optional[Dict]:
    """
    Get cached web search results.

    Args:
        query: Search query
        location: Optional location context

    Returns:
        Cached search results dict or None if not cached
    """
    cache_key = generate_cache_key(
        "web_search",
        query=query.lower().strip(),
        location=location.lower().strip() if location else None
    )
    result = cache.get(cache_key)
    if result:
        logger.debug(f"Cache HIT for web search: {query[:50]}...")
    return result


def set_web_search_cache(query: str, results: Dict, location: Optional[str] = None) -> None:
    """
    Cache web search results.

    Args:
        query: Search query
        results: Search results dictionary to cache
        location: Optional location context
    """
    cache_key = generate_cache_key(
        "web_search",
        query=query.lower().strip(),
        location=location.lower().strip() if location else None
    )
    ttl = getattr(settings, 'CACHE_TTL_WEB_SEARCH', 1800)
    cache.set(cache_key, results, ttl)
    logger.debug(f"Cached web search results for: {query[:50]}...")


# =============================================================================
# Utility Functions
# =============================================================================

def clear_all_cache() -> None:
    """Clear all cached data (for testing/admin)."""
    cache.clear()
    logger.info("All cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics (if supported by backend).

    Returns:
        Dictionary with cache stats or empty dict if not supported
    """
    try:
        # django-redis specific
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        info = conn.info()
        return {
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
    except Exception as e:
        logger.warning(f"Could not get cache stats: {e}")
        return {}
