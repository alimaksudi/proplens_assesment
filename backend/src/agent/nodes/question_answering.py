"""
Question answering node for handling user inquiries.

Includes web search fallback for project-specific queries about
external information (schools, transport, neighborhood, etc.).
"""

import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agent.state import ConversationState
from agent.tools import get_tavily_tool, should_search_web
from domain.models import Project

logger = logging.getLogger(__name__)

QA_PROMPT = """You are a property sales assistant for Silver Land Properties.

Context about properties the user has seen:
{property_context}

User's question: {question}

Conversation history:
{history}

Answer the user's question based on the property information available.
If asked about something not in the data (like schools, transport), say you don't have that specific information but can help with property details.
If the question is about a specific property, provide relevant details.
If they seem interested, gently suggest scheduling a viewing.

Keep response concise and helpful. Do not use emojis."""

QA_PROMPT_WITH_WEB_SEARCH = """You are a property sales assistant for Silver Land Properties.

Context about properties the user has seen:
{property_context}

User's question: {question}

Conversation history:
{history}

Web search results for additional context:
{web_results}

Answer the user's question using both the property information and web search results.
When using web search information, provide helpful details about schools, transport, neighborhood, etc.
Be helpful but note that web information may not be perfectly accurate.
If they seem interested in a property, gently suggest scheduling a viewing.

Keep response concise and helpful. Do not use emojis."""


def _extract_project_name(search_results: list, messages: list) -> str:
    """
    Extract project name from search results or conversation context.

    Args:
        search_results: List of property search results
        messages: Conversation messages

    Returns:
        Project name if found, empty string otherwise
    """
    # First, check search results for a project name
    if search_results:
        return search_results[0].get("project_name", "")

    # Check recent messages for project mentions
    for msg in reversed(messages[-6:]):
        content = msg.get("content", "")
        # Look for common patterns like "about X" or "regarding X"
        if "project" in content.lower():
            # Simple extraction - could be enhanced with NLP
            pass

    return ""


def _extract_location(search_results: list, preferences: dict) -> str:
    """
    Extract location from search results or preferences.

    Args:
        search_results: List of property search results
        preferences: User preferences

    Returns:
        Location if found, empty string otherwise
    """
    # Check search results
    if search_results:
        return search_results[0].get("city", "")

    # Check preferences
    if preferences:
        return preferences.get("location", "")

    return ""


async def answer_questions(state: ConversationState) -> ConversationState:
    """
    Answer user questions about properties or general inquiries.

    Includes web search fallback for project-specific queries about
    external information (schools, transport, neighborhood, etc.).
    """
    state["current_node"] = "answer_questions"

    messages = state.get("messages", [])
    search_results = state.get("search_results", [])
    preferences = state.get("preferences", {})
    tools_used = state.get("tools_used", [])

    # Get the question
    question = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            question = msg["content"]
            break

    # Check for goodbye messages (safety net for missed intent classification)
    question_lower = question.lower()
    goodbye_words = ["bye", "goodbye", "see you", "take care", "gotta go", "thanks bye"]
    if any(word in question_lower for word in goodbye_words):
        state["messages"].append({
            "role": "assistant",
            "content": "Thank you for exploring properties with me! Feel free to reach out whenever you're ready to continue. Have a great day!"
        })
        return state

    # Build property context
    property_context = "No specific properties discussed yet."
    if search_results:
        props = []
        for prop in search_results[:3]:
            props.append({
                "name": prop["project_name"],
                "city": prop["city"],
                "bedrooms": prop.get("bedrooms"),
                "price": prop.get("price_usd"),
                "features": prop.get("features", [])[:5],
                "description": prop.get("description", "")[:200]
            })
        property_context = json.dumps(props, indent=2)

    # Build conversation history
    history = "\n".join([
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:150]}"
        for m in messages[-6:]
    ])

    llm = ChatOpenAI(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        temperature=0.7
    )

    # Check if web search is needed for external information
    web_results_text = ""
    use_web_search = should_search_web(question)

    if use_web_search:
        logger.info(f"Web search triggered for question: {question}")
        tavily = get_tavily_tool()

        if tavily.is_available():
            # Extract context for better search
            project_name = _extract_project_name(search_results, messages)
            location = _extract_location(search_results, preferences)

            # Perform web search
            web_response = await tavily.search(
                query=question,
                project_name=project_name,
                location=location
            )

            if web_response.get("success"):
                tools_used.append("tavily_search")
                state["tools_used"] = tools_used

                # Format web results for LLM
                if web_response.get("answer"):
                    web_results_text = f"Summary: {web_response['answer']}\n\n"

                for result in web_response.get("results", []):
                    web_results_text += f"- {result['title']}: {result['content'][:200]}\n"

                logger.info("Web search results included in response")

    try:
        # Choose prompt based on whether web search was used
        if web_results_text:
            prompt = ChatPromptTemplate.from_template(QA_PROMPT_WITH_WEB_SEARCH)
            chain = prompt | llm
            response = await chain.ainvoke({
                "property_context": property_context,
                "question": question,
                "history": history,
                "web_results": web_results_text
            })
        else:
            prompt = ChatPromptTemplate.from_template(QA_PROMPT)
            chain = prompt | llm
            response = await chain.ainvoke({
                "property_context": property_context,
                "question": question,
                "history": history
            })

        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        state["messages"].append({
            "role": "assistant",
            "content": "I apologize, I'm having trouble accessing that information right now. Could you rephrase your question, or would you like me to help with something else?"
        })

    return state
