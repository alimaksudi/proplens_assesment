"""
Property search node using database queries and Vanna SQL tool.

Uses Django ORM for structured preference-based searches,
with Vanna AI Text-to-SQL as fallback for complex natural language queries.
"""

import logging
from typing import List, Dict, Any
from django.db.models import Q
from asgiref.sync import sync_to_async

from agent.state import ConversationState
from agent.tools import get_vanna_tool
from domain.models import Project

logger = logging.getLogger(__name__)


def build_search_query(preferences: Dict[str, Any]) -> Q:
    """Build Django Q object from preferences."""
    query = Q(is_valid=True)

    if preferences.get("city"):
        city = preferences["city"]
        query &= Q(city__icontains=city) | Q(country__iexact=city)

    if preferences.get("country"):
        query &= Q(country__iexact=preferences["country"])

    if preferences.get("bedrooms") is not None:
        bedrooms = preferences["bedrooms"]
        query &= Q(bedrooms=bedrooms) | Q(bedrooms=bedrooms + 1) | Q(bedrooms=bedrooms - 1)

    if preferences.get("budget_max"):
        query &= Q(price_usd__lte=preferences["budget_max"] * 1.2)

    if preferences.get("budget_min"):
        query &= Q(price_usd__gte=preferences["budget_min"] * 0.8)

    if preferences.get("property_type"):
        query &= Q(property_type__iexact=preferences["property_type"])

    if preferences.get("completion_status"):
        query &= Q(completion_status__iexact=preferences["completion_status"])

    return query


def calculate_match_score(project: Project, preferences: Dict[str, Any]) -> float:
    """Calculate how well a project matches preferences."""
    score = 0.0
    max_score = 0.0

    # City match (30%)
    if preferences.get("city"):
        max_score += 0.30
        if project.city and preferences["city"].lower() in project.city.lower():
            score += 0.30

    # Bedroom match (25%)
    if preferences.get("bedrooms") is not None:
        max_score += 0.25
        if project.bedrooms == preferences["bedrooms"]:
            score += 0.25
        elif project.bedrooms and abs(project.bedrooms - preferences["bedrooms"]) == 1:
            score += 0.15

    # Budget match (30%)
    if preferences.get("budget_max") or preferences.get("budget_min"):
        max_score += 0.30
        if project.price_usd:
            price = float(project.price_usd)
            budget_max = preferences.get("budget_max", float('inf'))
            budget_min = preferences.get("budget_min", 0)

            if budget_min <= price <= budget_max:
                score += 0.30
            elif price <= budget_max * 1.1:
                score += 0.20

    # Property type match (15%)
    if preferences.get("property_type"):
        max_score += 0.15
        if project.property_type == preferences["property_type"]:
            score += 0.15

    if max_score == 0:
        return 0.5

    return round(score / max_score, 2)


def _build_natural_language_query(preferences: Dict[str, Any], user_message: str) -> str:
    """
    Build a natural language query string from preferences and user message.
    Used for Vanna SQL tool when ORM search yields no results.
    """
    parts = []

    if preferences.get("bedrooms"):
        parts.append(f"{preferences['bedrooms']}-bedroom")

    if preferences.get("property_type"):
        parts.append(preferences["property_type"])
    else:
        parts.append("property")

    if preferences.get("city"):
        parts.append(f"in {preferences['city']}")

    if preferences.get("budget_max"):
        parts.append(f"under ${preferences['budget_max']:,.0f}")
    elif preferences.get("budget_min"):
        parts.append(f"over ${preferences['budget_min']:,.0f}")

    if preferences.get("completion_status"):
        parts.append(f"({preferences['completion_status']})")

    return " ".join(parts) if parts else user_message


def _format_vanna_results(vanna_results: List[Dict], preferences: Dict[str, Any]) -> List[Dict]:
    """
    Format Vanna SQL results to match expected property result structure.
    """
    results = []
    for row in vanna_results[:20]:
        try:
            # Map Vanna result columns to our expected format
            project_data = {
                "id": row.get("id"),
                "project_name": row.get("project_name", ""),
                "city": row.get("city", ""),
                "country": row.get("country", ""),
                "property_type": row.get("property_type"),
                "bedrooms": row.get("bedrooms"),
                "bathrooms": row.get("bathrooms"),
                "price_usd": float(row.get("price_usd")) if row.get("price_usd") else None,
                "area_sqm": float(row.get("area_sqm")) if row.get("area_sqm") else None,
                "completion_status": row.get("completion_status"),
                "features": row.get("features") or [],
                "facilities": row.get("facilities") or [],
                "description": row.get("description", "")[:300] if row.get("description") else None,
                "match_score": 0.7,  # Default score for Vanna results
            }

            # Calculate match score if we have preferences
            if preferences:
                # Create a mock project object for scoring
                class MockProject:
                    pass
                mock = MockProject()
                for k, v in project_data.items():
                    setattr(mock, k, v)
                project_data["match_score"] = calculate_match_score(mock, preferences)

            results.append(project_data)
        except Exception as e:
            logger.warning(f"Error formatting Vanna result: {e}")
            continue

    return results


async def search_properties(state: ConversationState) -> ConversationState:
    """
    Search for properties matching user preferences.

    Uses a two-tier approach:
    1. Primary: Django ORM for structured preference-based searches
    2. Fallback: Vanna AI Text-to-SQL for complex natural language queries

    This ensures reliable results while supporting flexible queries.
    """
    state["current_node"] = "search_properties"
    state["tools_used"].append("property_search")

    preferences = state.get("preferences", {})
    messages = state.get("messages", [])

    # Get latest user message for context
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    results = []

    # Primary search: Django ORM (wrapped with sync_to_async for async context)
    try:
        query = build_search_query(preferences)

        @sync_to_async
        def fetch_projects():
            return list(Project.objects.filter(query).order_by('-price_usd')[:20])

        projects = await fetch_projects()

        for project in projects:
            match_score = calculate_match_score(project, preferences)

            results.append({
                "id": project.id,
                "project_name": project.project_name,
                "city": project.city,
                "country": project.country,
                "property_type": project.property_type,
                "bedrooms": project.bedrooms,
                "bathrooms": project.bathrooms,
                "price_usd": float(project.price_usd) if project.price_usd else None,
                "area_sqm": float(project.area_sqm) if project.area_sqm else None,
                "completion_status": project.completion_status,
                "features": project.features or [],
                "facilities": project.facilities or [],
                "description": project.description[:300] if project.description else None,
                "match_score": match_score,
            })

        logger.info(f"ORM search found {len(results)} properties for preferences: {preferences}")

    except Exception as e:
        logger.error(f"ORM search error: {e}")

    # Fallback: Vanna SQL Tool (if ORM returns few/no results)
    if len(results) < 3:
        try:
            vanna_tool = get_vanna_tool()
            if vanna_tool.vanna is not None:
                # Build natural language query
                nl_query = _build_natural_language_query(preferences, user_message)
                logger.info(f"Trying Vanna SQL with query: {nl_query}")

                # Query using Vanna
                vanna_results = await vanna_tool.query_properties(nl_query)

                if vanna_results:
                    state["tools_used"].append("vanna_sql")
                    formatted = _format_vanna_results(vanna_results, preferences)

                    # Merge with existing results (avoid duplicates)
                    existing_ids = {r["id"] for r in results}
                    for item in formatted:
                        if item["id"] not in existing_ids:
                            results.append(item)
                            existing_ids.add(item["id"])

                    logger.info(f"Vanna SQL added {len(formatted)} results")

        except Exception as e:
            logger.warning(f"Vanna SQL fallback failed: {e}")

    # Sort by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)

    state["search_results"] = results[:10]
    state["recommended_projects"] = [r["id"] for r in results[:5]]

    if not results:
        logger.warning(f"No properties found for preferences: {preferences}")

    return state
