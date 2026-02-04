"""
Property recommendation node for presenting search results.
"""

import json
import logging
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.config import get_fallback_message
from agent.prompts import RECOMMENDATION_PROMPT, NO_RESULTS_PROMPT
from agent.utils.llm import get_conversational_llm

logger = logging.getLogger(__name__)


async def recommend_properties(state: ConversationState) -> ConversationState:
    """
    Present property recommendations to user.

    Generates natural language response with top matches.
    """
    state["current_node"] = "recommend_properties"

    results = state.get("search_results", [])
    preferences = state.get("preferences", {})

    llm = get_conversational_llm()

    try:
        if results:
            # Format top properties
            top_properties = []
            for prop in results[:3]:
                formatted = {
                    "name": prop["project_name"],
                    "city": prop["city"],
                    "bedrooms": prop["bedrooms"],
                    "bathrooms": prop["bathrooms"],
                    "price": f"${prop['price_usd']:,.0f}" if prop.get("price_usd") else "Price on request",
                    "area": f"{prop['area_sqm']:.0f} sqm" if prop.get("area_sqm") else None,
                    "type": prop.get("property_type"),
                    "status": prop.get("completion_status"),
                    "match_score": f"{prop['match_score']*100:.0f}%",
                }
                top_properties.append(formatted)

            prompt = ChatPromptTemplate.from_template(RECOMMENDATION_PROMPT)
            chain = prompt | llm

            response = await chain.ainvoke({
                "preferences": json.dumps(preferences),
                "properties": json.dumps(top_properties, indent=2)
            })

        else:
            prompt = ChatPromptTemplate.from_template(NO_RESULTS_PROMPT)
            chain = prompt | llm

            response = await chain.ainvoke({
                "preferences": json.dumps(preferences)
            })

        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")

        if results:
            # Fallback response with results
            top = results[0]
            fallback = f"I found some options for you. The top match is {top['project_name']} in {top['city']}"
            if top.get("price_usd"):
                fallback += f" at ${top['price_usd']:,.0f}"
            if top.get("bedrooms"):
                fallback += f" with {top['bedrooms']} bedrooms"
            fallback += ". Would you like more details or to schedule a viewing?"
        else:
            fallback = "I couldn't find exact matches for your criteria. Would you like to adjust your search? Perhaps consider a different location or budget range."

        state["messages"].append({
            "role": "assistant",
            "content": fallback
        })

    return state
