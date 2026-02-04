"""
Tavily web search tool for project-specific queries.

Used as a fallback when user asks about information not available
in the property database (e.g., schools, transport, neighborhood).
"""

import os
import logging
from typing import Dict, Any, Optional, List

from agent.utils.cache import get_cached_web_search, set_web_search_cache

logger = logging.getLogger(__name__)

# Tavily client import
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("Tavily not available. Web search will be disabled.")


class TavilySearchTool:
    """
    Web search tool using Tavily API for project-specific queries.

    Used as a fallback when the property database doesn't have
    information about schools, transport, neighborhood, etc.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Tavily search tool.

        Args:
            config: Configuration dictionary with api_key
        """
        self.config = config or {}
        self.api_key = self.config.get('api_key') or os.getenv('TAVILY_API_KEY')
        self.client = None

        if TAVILY_AVAILABLE and self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Tavily search tool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")

    def is_available(self) -> bool:
        """Check if Tavily search is available."""
        return self.client is not None

    async def search(
        self,
        query: str,
        project_name: Optional[str] = None,
        location: Optional[str] = None,
        max_results: int = 3
    ) -> Dict[str, Any]:
        """
        Search for project-specific information.

        Args:
            query: The user's question
            project_name: Optional project name for context
            location: Optional city/location for context
            max_results: Maximum number of results to return

        Returns:
            Dictionary with search results and metadata
        """
        if not self.client:
            logger.warning("Tavily client not available")
            return {
                "success": False,
                "results": [],
                "error": "Web search not configured"
            }

        try:
            # Check cache first
            cached = get_cached_web_search(query, location)
            if cached:
                logger.info("Using cached web search results")
                return cached

            # Build enhanced search query with project/location context
            search_query = self._build_search_query(query, project_name, location)
            logger.info(f"Tavily search query: {search_query}")

            # Execute search
            response = self.client.search(
                query=search_query,
                search_depth="basic",
                max_results=max_results,
                include_answer=True
            )

            # Format results
            results = self._format_results(response)

            logger.info(f"Tavily search returned {len(results['results'])} results")

            # Cache results for future requests
            set_web_search_cache(query, results, location)

            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return {
                "success": False,
                "results": [],
                "error": str(e)
            }

    def _build_search_query(
        self,
        query: str,
        project_name: Optional[str] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Build an enhanced search query with context.

        Args:
            query: Original user query
            project_name: Project name for context
            location: Location for context

        Returns:
            Enhanced search query string
        """
        parts = []

        # Add location context if available
        if location:
            parts.append(location)

        # Add project name if mentioned and not already in query
        if project_name and project_name.lower() not in query.lower():
            parts.append(project_name)

        # Add the original query
        parts.append(query)

        return " ".join(parts)

    def _format_results(self, response: Dict) -> Dict[str, Any]:
        """
        Format Tavily API response into a clean structure.

        Args:
            response: Raw Tavily API response

        Returns:
            Formatted results dictionary
        """
        results = []

        # Extract search results
        for result in response.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0)
            })

        return {
            "success": True,
            "answer": response.get("answer", ""),
            "results": results,
            "query": response.get("query", "")
        }


# Keywords that indicate external information is needed
EXTERNAL_INFO_KEYWORDS = [
    # Education
    'school', 'schools', 'university', 'college', 'education',
    # Transportation
    'transport', 'transportation', 'metro', 'subway', 'bus', 'train',
    'station', 'airport', 'commute',
    # Healthcare
    'hospital', 'clinic', 'medical', 'healthcare', 'doctor',
    # Lifestyle
    'restaurant', 'restaurants', 'cafe', 'dining', 'food',
    'mall', 'shopping', 'supermarket', 'grocery',
    'park', 'parks', 'gym', 'fitness', 'sports',
    'entertainment', 'cinema', 'theater',
    # Area info
    'neighborhood', 'neighbourhood', 'area', 'community',
    'nearby', 'close to', 'near', 'around', 'surrounding',
    'safety', 'crime', 'safe'
    # Note: Removed 'what is', 'tell me about', 'how is' - too generic
]

# Keywords that indicate a broad property search (should NOT trigger web search)
BROAD_SEARCH_KEYWORDS = [
    'show me', 'find', 'search', 'looking for', 'want',
    'bedroom', 'bedrooms', 'bathroom', 'bathrooms',
    'budget', 'price', 'under', 'below', 'above', 'between',
    'apartment', 'villa', 'house', 'property', 'properties',
    'available', 'for sale'
]


def needs_external_info(question: str) -> bool:
    """
    Check if question requires external information (web search).

    Args:
        question: User's question

    Returns:
        True if external info is needed
    """
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in EXTERNAL_INFO_KEYWORDS)


def is_broad_recommendation_query(question: str) -> bool:
    """
    Check if question is a broad property recommendation query.
    These should NOT trigger web search - only database search.

    Args:
        question: User's question

    Returns:
        True if it's a broad recommendation query
    """
    question_lower = question.lower()

    # Property search keywords (indicate user wants to find/see properties)
    search_intent_keywords = ['show me', 'find', 'search', 'looking for', 'want',
                              'available', 'for sale']

    # Property type terms that indicate a property search when combined with search intent
    property_types = ['apartment', 'apartments', 'villa', 'villas', 'house', 'houses',
                      'bedroom', 'bedrooms', 'bathroom', 'bathrooms']

    # Count how many broad search keywords are present
    broad_count = sum(1 for kw in BROAD_SEARCH_KEYWORDS if kw in question_lower)
    external_count = sum(1 for kw in EXTERNAL_INFO_KEYWORDS if kw in question_lower)

    # Check for search intent (e.g., "show me", "find", "looking for")
    has_search_intent = any(kw in question_lower for kw in search_intent_keywords)
    has_property_type = any(term in question_lower for term in property_types)

    # If user wants to FIND properties (has search intent + property type), it's a recommendation query
    # This excludes questions like "Is there transport near this property?" which don't have search intent
    if has_search_intent and has_property_type:
        return True

    # Tie goes to broad (database search) to avoid unnecessary web searches
    return broad_count >= external_count


def should_search_web(question: str) -> bool:
    """
    Determine if web search should be invoked.

    Web search is invoked when:
    - Question contains external info keywords
    - Question is NOT a broad property recommendation query

    Args:
        question: User's question

    Returns:
        True if web search should be used
    """
    return needs_external_info(question) and not is_broad_recommendation_query(question)


# Singleton instance
_tavily_instance: Optional[TavilySearchTool] = None


def get_tavily_tool() -> TavilySearchTool:
    """Get or create Tavily tool singleton."""
    global _tavily_instance

    if _tavily_instance is None:
        _tavily_instance = TavilySearchTool()

    return _tavily_instance
