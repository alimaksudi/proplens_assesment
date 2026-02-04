"""
LangGraph orchestrator for the property sales agent.

Implements a state machine for conversation flow with conditional
routing based on user intent and conversation state.
"""

import os
import copy
import logging
from typing import Dict, Optional, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from .state import ConversationState, create_initial_state, update_state_timestamp
from .schemas import validate_message
from .nodes import (
    greet_user,
    classify_intent,
    discover_preferences,
    search_properties,
    recommend_properties,
    answer_questions,
    propose_booking,
    capture_lead_details,
    confirm_booking,
    handle_error,
    handle_goodbye,
)

logger = logging.getLogger(__name__)


class PropertyAgentGraph:
    """
    LangGraph orchestrator for conversational property agent.

    Manages the conversation flow through a state machine, delegating
    to specialized nodes for each conversation step.
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize the agent graph.

        Args:
            llm: Optional ChatOpenAI instance. If not provided, will
                 create one using environment variables.
        """
        self.llm = llm or ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=0.7,
        )
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        """Build the conversation flow graph."""
        graph = StateGraph(ConversationState)

        # Add nodes
        graph.add_node("greeting", greet_user)
        graph.add_node("classify_intent", classify_intent)
        graph.add_node("discover_preferences", discover_preferences)
        graph.add_node("search_properties", search_properties)
        graph.add_node("recommend_properties", recommend_properties)
        graph.add_node("answer_questions", answer_questions)
        graph.add_node("propose_booking", propose_booking)
        graph.add_node("capture_lead", capture_lead_details)
        graph.add_node("confirm_booking", confirm_booking)
        graph.add_node("handle_error", handle_error)
        graph.add_node("goodbye", handle_goodbye)

        # Set entry point
        graph.set_entry_point("greeting")

        # Add edges from greeting
        graph.add_edge("greeting", "classify_intent")

        # Conditional routing from classify_intent
        graph.add_conditional_edges(
            "classify_intent",
            self._route_after_classification,
            {
                "discover": "discover_preferences",
                "search": "search_properties",
                "recommend": "recommend_properties",
                "question": "answer_questions",
                "booking": "propose_booking",
                "provide_contact": "capture_lead",
                "error": "handle_error",
                "goodbye": "goodbye",
                "end": END,
            }
        )

        # From discover_preferences
        graph.add_conditional_edges(
            "discover_preferences",
            self._should_search_properties,
            {
                "search": "search_properties",
                "continue": END,
            }
        )

        # From search_properties
        graph.add_edge("search_properties", "recommend_properties")

        # From recommend_properties
        graph.add_edge("recommend_properties", END)

        # From answer_questions
        graph.add_conditional_edges(
            "answer_questions",
            self._after_question,
            {
                "booking": "propose_booking",
                "search": "search_properties",
                "end": END,
            }
        )

        # From propose_booking
        graph.add_edge("propose_booking", "capture_lead")

        # From capture_lead
        graph.add_conditional_edges(
            "capture_lead",
            self._lead_capture_complete,
            {
                "confirm": "confirm_booking",
                "continue": END,
            }
        )

        # From confirm_booking
        graph.add_edge("confirm_booking", END)

        # From goodbye
        graph.add_edge("goodbye", END)

        # From handle_error
        graph.add_edge("handle_error", END)

        return graph

    def _route_after_classification(
        self,
        state: ConversationState
    ) -> Literal["discover", "search", "recommend", "question", "booking", "provide_contact", "error", "end"]:
        """Route conversation based on classified intent."""
        intent = state.get("user_intent", "other")

        if state.get("error_message"):
            return "error"

        if intent == "greeting":
            return "discover"

        elif intent == "share_preferences":
            return "discover"

        elif intent == "ask_question":
            return "question"

        elif intent == "request_recommendations":
            if state.get("preferences_complete") or state.get("preferences", {}).get("city"):
                return "search"
            else:
                return "discover"

        elif intent == "express_interest":
            if state.get("search_results"):
                return "booking"
            else:
                return "recommend"

        elif intent == "book_viewing":
            return "booking"

        elif intent == "provide_contact":
            return "provide_contact"

        elif intent == "goodbye":
            return "goodbye"

        elif intent == "clarify":
            # User is clarifying - route to Q&A to handle clarification
            return "question"

        else:
            # "other" or unrecognized intents
            # Smart fallback: If we have some conversation context, try to answer
            # Only go to preference_discovery if this is truly a new conversation
            messages = state.get("messages", [])

            # First check for goodbye words (safety net for missed intent classification)
            if messages:
                last_user_msg = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        last_user_msg = msg.get("content", "").lower()
                        break

                goodbye_words = ["bye", "goodbye", "see you", "take care", "gotta go", "thanks bye", "thank you bye", "thanks", "thank you"]
                if any(word in last_user_msg for word in goodbye_words):
                    return "goodbye"

            has_context = len(messages) > 2  # More than just greeting exchange

            if has_context:
                # We have conversation context, try to answer the question
                return "question"
            elif state.get("preferences", {}).get("city"):
                # Has preferences, try to search
                return "search"
            else:
                # True new conversation, start preference discovery
                return "discover"

    def _should_search_properties(
        self,
        state: ConversationState
    ) -> Literal["search", "continue"]:
        """Determine if we have enough preferences to search."""
        prefs = state.get("preferences", {})

        has_city = bool(prefs.get("city"))
        has_bedrooms = prefs.get("bedrooms") is not None
        has_budget = prefs.get("budget_max") is not None or prefs.get("budget_min") is not None

        # Also check if preferences_complete was set (e.g., user said "any price")
        preferences_complete = state.get("preferences_complete", False)

        # Search if: has city AND (has bedrooms OR has budget OR marked as complete)
        if has_city and (has_bedrooms or has_budget or preferences_complete):
            return "search"

        return "continue"

    def _after_question(
        self,
        state: ConversationState
    ) -> Literal["booking", "search", "end"]:
        """Decide next step after answering a question."""
        messages = state.get("messages", [])
        if not messages:
            return "end"

        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "").lower()
                break

        # Check for goodbye words first
        goodbye_words = ["bye", "goodbye", "see you", "take care", "thanks bye"]
        if any(word in last_user_msg for word in goodbye_words):
            return "end"

        if any(word in last_user_msg for word in ["book", "schedule", "viewing", "visit"]):
            return "booking"

        if any(word in last_user_msg for word in ["show me", "other options", "more", "different"]):
            return "search"

        return "end"

    def _lead_capture_complete(
        self,
        state: ConversationState
    ) -> Literal["confirm", "continue"]:
        """Check if we have all required lead information."""
        lead = state.get("lead_data", {})
        # Only require first_name + email; last_name is optional (parsed from full name)
        required_fields = ["first_name", "email"]
        has_required = all(lead.get(field) for field in required_fields)

        if has_required and state.get("selected_project_id"):
            return "confirm"

        return "continue"

    async def process_message(
        self,
        conversation_id: str,
        message: str,
        existing_state: Optional[ConversationState] = None
    ) -> ConversationState:
        """
        Process a user message through the graph.

        Args:
            conversation_id: Unique conversation identifier
            message: User's message text
            existing_state: Previous conversation state (if resuming)

        Returns:
            Updated conversation state
        """
        # Validate and sanitize user message
        validated_message = validate_message(message)

        if existing_state:
            # Use deepcopy to prevent race conditions with nested dicts
            state = copy.deepcopy(existing_state)
            state["messages"].append({"role": "user", "content": validated_message})
        else:
            state = create_initial_state(conversation_id)
            state["messages"].append({"role": "user", "content": validated_message})

        state = update_state_timestamp(state)
        state["tools_used"] = []

        try:
            result = await self.compiled_graph.ainvoke(state)
            return result
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            state["error_message"] = str(e)
            state["messages"].append({
                "role": "assistant",
                "content": "I apologize, but I encountered an issue. Could you please try again?"
            })
            return state


# Singleton instance
_agent_graph: Optional[PropertyAgentGraph] = None


def get_agent_graph() -> PropertyAgentGraph:
    """Get or create the agent graph singleton."""
    global _agent_graph

    if _agent_graph is None:
        _agent_graph = PropertyAgentGraph()

    return _agent_graph
