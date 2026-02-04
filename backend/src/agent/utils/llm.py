"""
Shared LLM instance management for reduced overhead.

This module provides factory functions to get shared LLM instances,
avoiding the overhead of creating new instances for each request.
"""
import os
import logging
from typing import Optional

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# Cache for LLM instances by configuration
_llm_instances = {}


def get_llm(temperature: float = 0.7, model: Optional[str] = None) -> ChatOpenAI:
    """
    Get or create a shared LLM instance.

    Reuses instances with same temperature/model to reduce overhead.

    Args:
        temperature: LLM temperature (0.0 = deterministic, 1.0 = creative)
        model: Model name (defaults to OPENAI_MODEL env var)

    Returns:
        ChatOpenAI instance
    """
    model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    cache_key = f"{model}:{temperature}"

    if cache_key not in _llm_instances:
        _llm_instances[cache_key] = ChatOpenAI(
            model=model,
            temperature=temperature,
        )
        logger.debug(f"Created new LLM instance: {cache_key}")

    return _llm_instances[cache_key]


def get_classifier_llm() -> ChatOpenAI:
    """
    Get LLM configured for classification (temperature=0).

    Returns:
        ChatOpenAI instance optimized for classification tasks
    """
    return get_llm(temperature=0)


def get_conversational_llm() -> ChatOpenAI:
    """
    Get LLM configured for conversation (temperature=0.7).

    Returns:
        ChatOpenAI instance optimized for conversational responses
    """
    return get_llm(temperature=0.7)


def clear_llm_cache() -> None:
    """
    Clear all cached LLM instances.

    Useful for testing or when configuration changes.
    """
    global _llm_instances
    _llm_instances = {}
    logger.info("LLM instance cache cleared")
