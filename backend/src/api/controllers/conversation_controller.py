"""
Conversation controller for handling chat interactions.
"""

import time
import logging
import asyncio
from typing import List, Optional
from uuid import uuid4, UUID

from ninja_extra import api_controller, http_post, http_get
from ninja import Schema
from django.http import HttpRequest

from api.schemas.request import ChatRequest
from api.schemas.response import (
    ChatResponse,
    ConversationResponse,
    PropertyRecommendation,
    ResponseContent,
    StructuredData,
    Metadata,
    ErrorResponse,
)
from domain.models import Conversation, Project
from agent.graph import get_agent_graph
from agent.state import create_initial_state

logger = logging.getLogger(__name__)


@api_controller('/conversations', tags=['Conversations'])
class ConversationController:
    """Controller for conversation management and chat interactions."""

    @http_post('/', response={201: ConversationResponse, 400: ErrorResponse})
    def create_conversation(self, request: HttpRequest):
        """
        Create a new conversation session.

        Returns a conversation ID to be used in subsequent chat requests.
        """
        try:
            conversation = Conversation.objects.create(
                state=create_initial_state(str(uuid4()))
            )

            # Update state with actual conversation ID
            conversation.state['conversation_id'] = str(conversation.id)
            conversation.save()

            logger.info(f"Created conversation: {conversation.id}")

            return 201, {
                "conversation_id": str(conversation.id),
                "created_at": conversation.created_at,
            }

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return 400, {
                "error": "creation_failed",
                "message": str(e),
            }

    @http_get('/{conversation_id}', response={200: dict, 404: ErrorResponse})
    def get_conversation(self, request: HttpRequest, conversation_id: str):
        """
        Get conversation details and state.
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return 200, conversation.to_dict()

        except Conversation.DoesNotExist:
            return 404, {
                "error": "not_found",
                "message": f"Conversation {conversation_id} not found",
            }


@api_controller('/agents', tags=['Agent'])
class AgentController:
    """Controller for agent chat interactions."""

    @http_post('/chat', response={200: ChatResponse, 400: ErrorResponse, 404: ErrorResponse})
    def chat(self, request: HttpRequest, payload: ChatRequest):
        """
        Send a message to the property agent and receive a response.

        This endpoint processes the user message through the LangGraph
        agent and returns the assistant's response along with any
        property recommendations.
        """
        start_time = time.time()

        try:
            # Validate conversation exists
            try:
                conversation = Conversation.objects.get(id=payload.conversation_id)
            except Conversation.DoesNotExist:
                return 404, {
                    "error": "conversation_not_found",
                    "message": f"Conversation {payload.conversation_id} not found",
                }

            # Get existing state
            existing_state = conversation.state

            # Process message through agent
            agent = get_agent_graph()

            # Run async in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result_state = loop.run_until_complete(
                    agent.process_message(
                        conversation_id=payload.conversation_id,
                        message=payload.message,
                        existing_state=existing_state,
                    )
                )
            finally:
                loop.close()

            # Save updated state
            conversation.state = result_state
            conversation.save()

            # Extract response
            messages = result_state.get("messages", [])
            assistant_message = ""
            for msg in reversed(messages):
                if msg["role"] == "assistant":
                    assistant_message = msg["content"]
                    break

            # Build recommendations from search results
            recommendations = self._build_recommendations(
                result_state.get("search_results", [])
            )

            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)

            # Build response
            response = ChatResponse(
                conversation_id=payload.conversation_id,
                response=ResponseContent(
                    message=assistant_message,
                    intent=result_state.get("user_intent"),
                    structured_data=StructuredData(
                        preferences_captured=result_state.get("preferences"),
                        next_questions=None,
                        booking={
                            "booking_id": result_state.get("booking_id"),
                            "status": "confirmed" if result_state.get("booking_confirmed") else "pending",
                        } if result_state.get("booking_id") else None,
                    ),
                    state=result_state.get("current_node", "unknown"),
                ),
                recommendations=recommendations,
                metadata=Metadata(
                    processing_time_ms=processing_time,
                    tools_used=result_state.get("tools_used", []),
                ),
            )

            logger.info(
                f"Processed message for {payload.conversation_id} "
                f"in {processing_time}ms"
            )

            return 200, response

        except Exception as e:
            logger.error(f"Error processing chat: {e}", exc_info=True)
            return 400, {
                "error": "processing_error",
                "message": "An error occurred processing your message. Please try again.",
                "details": {"error_type": type(e).__name__}
            }

    def _build_recommendations(
        self,
        search_results: List[dict]
    ) -> List[PropertyRecommendation]:
        """Build property recommendations from search results."""
        recommendations = []

        for result in search_results[:5]:
            rec = PropertyRecommendation(
                id=result.get("id", 0),
                project_name=result.get("project_name", ""),
                city=result.get("city", ""),
                country=result.get("country", ""),
                property_type=result.get("property_type"),
                bedrooms=result.get("bedrooms"),
                bathrooms=result.get("bathrooms"),
                price_usd=result.get("price_usd"),
                area_sqm=result.get("area_sqm"),
                completion_status=result.get("completion_status"),
                key_features=(result.get("features", []) + result.get("facilities", []))[:5],
                match_score=result.get("match_score"),
                description=result.get("description"),
            )
            recommendations.append(rec)

        return recommendations
