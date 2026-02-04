# Agent Architecture Decision
## Single Agent vs Multi-Agent Approach

---

## Executive Summary

**Core Architecture:** **Cyclic State Machine Orchestration** (powered by LangGraph)

**Strategy:** **Hybrid Retrieval (RAG++)**
- **Orchestrator**: LangGraph state machine for deterministic flow control
- **Text-to-SQL**: Vanna AI for ultra-precise database querying
- **Direct ORM**: Django-native filtering for fast property lookups
- **Web Search**: Tavily for real-time neighborhood and amenity context

**Reasoning:**
- **Lead-Level Maturity**: Moves beyond simple linear flow to handle non-linear real-world conversations.
- **Deterministic Reliability**: Unlike pure "Agentic" loops, our cyclic graph offers predictable state transitions.
- **Data Grounding**: Hybrid retrieval prevents hallucinations by ensuring every fact is backed by Postgres or Tavily.
- **Modular Scalability**: Tool-agents are isolated, making the system easy to extend and debug.

---

## Architecture Options Comparison

### Option 1: Single Agent with Tools (Basic)

```
┌──────────────────────────────────┐
│     LangGraph Orchestrator       │
│                                  │
│  greet → discover → search →    │
│  recommend → answer → book      │
│                                  │
│  Tools:                          │
│  - vanna_sql_tool()             │
│  - web_search_tool()            │
│  - booking_tool()               │
└──────────────────────────────────┘
```

**Pros:**
- ✅ Simplest to implement
- ✅ Lowest latency (single LLM call per turn)
- ✅ Easiest to debug
- ✅ Sufficient for linear workflows

**Cons:**
- ❌ Less modular
- ❌ Hard to scale specific capabilities
- ❌ All logic in one graph
- ❌ Doesn't demonstrate advanced architecture

**Best for:** Proof of concepts, simple workflows

---

### Option 2: Pure Multi-Agent (Advanced)

```
┌─────────────────────────────────────────┐
│        Supervisor Agent                 │
│  (Routes to specialized agents)         │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
    ▼             ▼          ▼          ▼
┌────────┐  ┌─────────┐ ┌────────┐ ┌────────┐
│Search  │  │Question │ │Booking │ │Clarify │
│Agent   │  │Agent    │ │Agent   │ │Agent   │
└────────┘  └─────────┘ └────────┘ └────────┘
   │             │          │          │
   ▼             ▼          ▼          ▼
[Vanna]      [Web+DB]   [CRM API]  [Context]
```

**Pros:**
- ✅ Highly modular (each agent is independent)
- ✅ Parallel execution possible
- ✅ Easy to extend (add new agents)
- ✅ Team-based development (different devs per agent)

**Cons:**
- ❌ Complex coordination logic
- ❌ Higher latency (multiple LLM calls)
- ❌ More expensive (each agent = API call)
- ❌ Harder to debug (distributed tracing needed)
- ❌ Over-engineering for this assessment

**Best for:** Large-scale production systems with complex workflows

---

### Option 3: Hybrid (Recommended) ⭐

```
┌────────────────────────────────────────────┐
│     LangGraph Orchestrator (Main Agent)    │
│                                            │
│  Nodes:                                    │
│  - greet_user                              │
│  - classify_intent                         │
│  - discover_preferences                    │
│  - answer_questions ←─────┐               │
│  - propose_booking         │               │
│  - confirm_booking         │               │
└──────────┬─────────────────┼───────────────┘
           │                 │
           ▼                 │
   ┌───────────────┐         │
   │ Tool-Agents   │         │
   │ (Specialized) │         │
   └───┬───────────┘         │
       │                     │
   ┌───┴────┬────────┬───────┴────┐
   │        │        │             │
   ▼        ▼        ▼             ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│Search  │ │Web   │ │Booking │ │Clarify   │
│Tool-   │ │Search│ │Tool-   │ │Tool-     │
│Agent   │ │Tool- │ │Agent   │ │Agent     │
│        │ │Agent │ │        │ │          │
└────────┘ └──────┘ └────────┘ └──────────┘
```

**Architecture:**
- **Main orchestrator**: LangGraph state machine (handles conversation flow)
- **Tool-agents**: Specialized mini-agents called by main orchestrator
- **Clear separation**: Orchestration logic vs. domain logic

**Pros:**
- ✅ Modular (tool-agents are independent)
- ✅ Reasonable complexity (demonstrates senior thinking)
- ✅ Debuggable (main flow is linear, tools are isolated)
- ✅ Scalable (can parallelize tool-agent calls)
- ✅ Best of both worlds

**Cons:**
- ⚠️ Slightly more complex than basic approach
- ⚠️ Requires clear interface design between components

**Best for:** This assessment ⭐

---

## Hybrid Architecture Implementation

### Main Orchestrator (LangGraph)

```python
# agent/graph.py

from langgraph.graph import StateGraph, END
from agent.state import ConversationState
from agent.tool_agents import (
    SearchToolAgent,
    QuestionToolAgent,
    BookingToolAgent,
    ClarificationToolAgent
)

class PropertyAgentGraph:
    """
    Main orchestrator: Manages conversation flow
    Delegates specialized tasks to tool-agents
    """
    
    def __init__(self, llm):
        self.llm = llm
        
        # Initialize tool-agents
        self.search_agent = SearchToolAgent(llm)
        self.question_agent = QuestionToolAgent(llm)
        self.booking_agent = BookingToolAgent(llm)
        self.clarify_agent = ClarificationToolAgent(llm)
        
        self.graph = self._build_graph()
    
    def _build_graph(self):
        graph = StateGraph(ConversationState)
        
        # Core conversation nodes
        graph.add_node("greet", self.greet_user)
        graph.add_node("classify_intent", self.classify_intent)
        graph.add_node("discover_preferences", self.discover_preferences)
        graph.add_node("search_properties", self.search_properties)  # Uses search_agent
        graph.add_node("answer_questions", self.answer_questions)    # Uses question_agent
        graph.add_node("propose_booking", self.propose_booking)
        graph.add_node("confirm_booking", self.confirm_booking)      # Uses booking_agent
        
        # Define edges
        graph.set_entry_point("greet")
        # ... (same as before, but nodes delegate to tool-agents)
        
        return graph.compile()
    
    async def search_properties(self, state: ConversationState) -> ConversationState:
        """
        Orchestrator node: Delegates property search to SearchToolAgent
        """
        preferences = state["preferences"]
        
        # Delegate to search tool-agent
        search_results = await self.search_agent.search(preferences)
        
        # Update state with results
        state["search_results"] = search_results
        state["recommended_projects"] = [r["id"] for r in search_results[:3]]
        
        # Generate response using main LLM
        response = self._format_search_response(search_results)
        state["messages"].append({"role": "assistant", "content": response})
        
        return state
    
    async def answer_questions(self, state: ConversationState) -> ConversationState:
        """
        Orchestrator node: Delegates question answering to QuestionToolAgent
        """
        last_message = state["messages"][-1]["content"]
        context = {
            "recommended_projects": state["recommended_projects"],
            "conversation_history": state["messages"]
        }
        
        # Delegate to question tool-agent
        answer = await self.question_agent.answer(last_message, context)
        
        # Update state
        state["messages"].append({"role": "assistant", "content": answer})
        
        return state
```

### Tool-Agents (Specialized)

#### 1. Search Tool-Agent

```python
# agent/tool_agents/search_agent.py

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from agent.tools.vanna_sql_tool import get_vanna_tool

class SearchToolAgent:
    """
    Specialized agent for property search
    
    Responsibilities:
    - Convert preferences to natural language query
    - Use Vanna to generate SQL
    - Execute query and return results
    - Handle "no results" case (suggest alternatives)
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.vanna = get_vanna_tool()
        
        self.query_builder_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a property search query specialist.
            Convert user preferences into a natural language search query
            that can be passed to a SQL generation system.
            
            Examples:
            Preferences: {{"city": "Chicago", "bedrooms": 2, "budget_max": 1000000}}
            Query: "Find 2-bedroom apartments in Chicago under $1,000,000"
            
            Preferences: {{"city": "New York", "property_type": "villa"}}
            Query: "Show me villas in New York"
            """),
            ("user", "Preferences: {preferences}\nGenerate search query:")
        ])
    
    async def search(self, preferences: Dict) -> List[Dict]:
        """
        Main search method
        
        Args:
            preferences: User's property preferences
        
        Returns:
            List of matching properties (up to 10)
        """
        
        # Step 1: Convert preferences to natural language query
        query = await self._build_query(preferences)
        
        # Step 2: Use Vanna to search database
        results = await self.vanna.query_properties(query)
        
        # Step 3: If no results, try fuzzy search
        if not results:
            results = await self._fuzzy_search(preferences)
        
        # Step 4: Rank and return top 10
        ranked_results = self._rank_results(results, preferences)
        
        return ranked_results[:10]
    
    async def _build_query(self, preferences: Dict) -> str:
        """Build natural language query from preferences"""
        chain = self.query_builder_prompt | self.llm
        response = await chain.ainvoke({"preferences": str(preferences)})
        return response.content
    
    async def _fuzzy_search(self, preferences: Dict) -> List[Dict]:
        """
        Fallback: Fuzzy search when exact match fails
        
        Strategy:
        1. Relax bedroom requirement (±1)
        2. Relax budget (±20%)
        3. Expand to nearby cities
        """
        
        fuzzy_prefs = preferences.copy()
        
        # Relax bedrooms
        if "bedrooms" in fuzzy_prefs:
            bedrooms = fuzzy_prefs["bedrooms"]
            fuzzy_prefs["bedrooms_range"] = [bedrooms - 1, bedrooms, bedrooms + 1]
            del fuzzy_prefs["bedrooms"]
        
        # Relax budget
        if "budget_max" in fuzzy_prefs:
            budget = fuzzy_prefs["budget_max"]
            fuzzy_prefs["budget_max"] = budget * 1.2  # +20%
        
        query = await self._build_query(fuzzy_prefs)
        results = await self.vanna.query_properties(query)
        
        # Mark as fuzzy match
        for result in results:
            result["match_type"] = "fuzzy"
        
        return results
    
    def _rank_results(self, results: List[Dict], preferences: Dict) -> List[Dict]:
        """
        Rank results by relevance to preferences
        
        Scoring factors:
        - Exact city match: +10 points
        - Exact bedroom match: +8 points
        - Within budget: +5 points
        - Has description: +2 points
        - Has features: +1 point
        """
        
        for result in results:
            score = 0
            
            # City match
            if result.get("city") == preferences.get("city"):
                score += 10
            
            # Bedroom match
            if result.get("bedrooms") == preferences.get("bedrooms"):
                score += 8
            
            # Budget match
            if "budget_max" in preferences:
                if result.get("price_usd") and result["price_usd"] <= preferences["budget_max"]:
                    score += 5
            
            # Data quality
            if result.get("description"):
                score += 2
            if result.get("features"):
                score += 1
            
            result["relevance_score"] = score
        
        # Sort by score (descending)
        return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)
```

#### 2. Question Tool-Agent

```python
# agent/tool_agents/question_agent.py

from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from agent.tools.web_search_tool import get_web_search_tool

class QuestionToolAgent:
    """
    Specialized agent for answering property questions
    
    Responsibilities:
    - Classify question type (factual, opinion, comparison)
    - Route to appropriate source (database, web search, decline)
    - Generate natural answer
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.web_search = get_web_search_tool()
        
        self.classifier_prompt = ChatPromptTemplate.from_messages([
            ("system", """Classify the user's question:
            - "database": Can be answered from property database
            - "web_search": Requires external information (location, schools, transport)
            - "opinion": Asking for recommendation/advice (decline politely)
            - "unclear": Question is ambiguous (ask for clarification)
            """),
            ("user", "Question: {question}\nClassification:")
        ])
    
    async def answer(self, question: str, context: Dict) -> str:
        """
        Answer user's question about properties
        
        Args:
            question: User's question
            context: Conversation context (recommended projects, history)
        
        Returns:
            Answer string
        """
        
        # Step 1: Classify question
        question_type = await self._classify_question(question)
        
        # Step 2: Route to appropriate handler
        if question_type == "database":
            return await self._answer_from_database(question, context)
        elif question_type == "web_search":
            return await self._answer_from_web(question, context)
        elif question_type == "opinion":
            return self._decline_opinion()
        else:  # unclear
            return self._ask_clarification()
    
    async def _classify_question(self, question: str) -> str:
        """Classify question type"""
        chain = self.classifier_prompt | self.llm
        response = await chain.ainvoke({"question": question})
        return response.content.strip().lower()
    
    async def _answer_from_database(self, question: str, context: Dict) -> str:
        """Answer using database information"""
        # Get project details from context
        project_ids = context.get("recommended_projects", [])
        
        # Query database for details
        # ... (implementation)
        
        # Generate natural answer
        answer_prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the question based on these project details: {details}"),
            ("user", "{question}")
        ])
        
        chain = answer_prompt | self.llm
        response = await chain.ainvoke({
            "details": "...",  # project details
            "question": question
        })
        
        return response.content
    
    async def _answer_from_web(self, question: str, context: Dict) -> str:
        """Answer using web search"""
        # Get project name from context
        # ... 
        
        # Perform web search
        search_results = await self.web_search.search(f"{project_name} {question}")
        
        # Synthesize answer from search results
        # ...
        
        return answer
    
    def _decline_opinion(self) -> str:
        """Politely decline opinion questions"""
        return """I can provide factual information about properties, but I can't 
        give investment advice or personal recommendations. However, I'd be happy to 
        share objective details about any property that interests you, or connect you 
        with our sales team for personalized guidance."""
    
    def _ask_clarification(self) -> str:
        """Ask for clarification"""
        return """I want to make sure I understand your question correctly. 
        Could you rephrase or provide more details?"""
```

#### 3. Booking Tool-Agent

```python
# agent/tool_agents/booking_agent.py

from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from agent.tools.booking_tool import get_booking_tool

class BookingToolAgent:
    """
    Specialized agent for booking management
    
    Responsibilities:
    - Validate lead information
    - Handle progressive lead capture
    - Create bookings in database
    - Generate confirmation messages
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.booking_tool = get_booking_tool()
    
    async def create_booking(
        self,
        lead_data: Dict,
        project_id: int,
        conversation_id: str
    ) -> Dict:
        """
        Create booking with validation
        
        Returns:
            {
                "success": bool,
                "booking_id": int,
                "message": str,
                "missing_fields": List[str]
            }
        """
        
        # Validate lead data
        is_complete, missing = self._validate_lead_data(lead_data)
        
        if not is_complete:
            return {
                "success": False,
                "message": f"I need your {', '.join(missing)} to complete the booking.",
                "missing_fields": missing
            }
        
        # Create booking
        booking = await self.booking_tool.create_booking(
            lead_data=lead_data,
            project_id=project_id,
            conversation_id=conversation_id
        )
        
        # Generate confirmation
        message = await self.booking_tool.get_confirmation_message(booking)
        
        return {
            "success": True,
            "booking_id": booking.id,
            "message": message,
            "missing_fields": []
        }
    
    def _validate_lead_data(self, lead_data: Dict) -> tuple[bool, List[str]]:
        """Validate completeness of lead data"""
        required = ["first_name", "last_name", "email"]
        missing = [field for field in required if not lead_data.get(field)]
        return len(missing) == 0, missing
```

#### 4. Clarification Tool-Agent

```python
# agent/tool_agents/clarify_agent.py

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class ClarificationToolAgent:
    """
    Specialized agent for query clarification
    
    Responsibilities:
    - Detect ambiguous queries
    - Generate clarifying questions
    - Rewrite queries based on clarifications
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
        self.ambiguity_detector = ChatPromptTemplate.from_messages([
            ("system", """Detect if the query is ambiguous:
            Ambiguous: "Show me properties" (missing city, bedrooms, budget)
            Clear: "Show me 2-bedroom apartments in Chicago under $1M"
            
            Return "ambiguous" or "clear" and explain why.
            """),
            ("user", "Query: {query}")
        ])
    
    async def check_clarity(self, query: str) -> Dict:
        """
        Check if query is clear enough
        
        Returns:
            {
                "is_clear": bool,
                "missing_info": List[str],
                "clarifying_question": str
            }
        """
        
        chain = self.ambiguity_detector | self.llm
        response = await chain.ainvoke({"query": query})
        
        # Parse response
        # ...
        
        return {
            "is_clear": False,
            "missing_info": ["city", "bedrooms"],
            "clarifying_question": "What city are you interested in, and how many bedrooms?"
        }
```

---

## Implementation Strategy

### Phase 1: Start with Single Agent (Days 1-4)
Build basic LangGraph with inline tools

### Phase 2: Extract Tool-Agents (Days 5-6)
Refactor tools into specialized agents:
1. Move Vanna logic → SearchToolAgent
2. Move Q&A logic → QuestionToolAgent
3. Move booking logic → BookingToolAgent

### Phase 3: Add Advanced Features (Days 7-8)
- Query clarification (ClarificationToolAgent)
- Self-correction in search
- Parallel tool execution

---

## Benefits of Hybrid Approach

1. **Modularity**: Each tool-agent is independently testable
2. **Clarity**: Main orchestrator focuses on conversation flow
3. **Extensibility**: Easy to add new tool-agents
4. **Debuggability**: Can test each component separately
5. **Demonstrates senior thinking**: Shows architectural maturity

---

## Comparison to References

### LangGraph Multi-Agent Pattern
Your reference: https://docs.langchain.com/oss/python/langgraph/workflows-agents

**What we're using:**
- ✅ StateGraph for main orchestrator
- ✅ Conditional routing between nodes
- ✅ Checkpointing for state persistence
- ✅ Tool calling from nodes

**What we're NOT using:**
- ❌ Supervisor agent (not needed for this flow)
- ❌ Agent-to-agent communication (our tools don't talk to each other)
- ❌ Map-reduce parallelization (not needed for this dataset size)

### Vanna AI Integration
Your reference: https://vanna.ai/docs/configure

**What we're using:**
- ✅ ChromaDB for training data storage
- ✅ Training with DDL + example pairs
- ✅ `generate_sql()` for query generation
- ✅ `run_sql()` for execution

**Enhancement:**
- Wrap Vanna in SearchToolAgent for:
  - Fuzzy search fallback
  - Result ranking
  - Error handling

### Tavily Search
Your reference: https://github.com/tavily-ai/tavily-chat

**What we're using:**
- ✅ Tavily for web search (project-specific queries)
- ✅ Rate limiting (max 2 searches per conversation)
- ✅ Query enhancement (add project name to search)

**Enhancement:**
- Wrap in QuestionToolAgent for:
  - Question classification
  - Search vs. database routing
  - Answer synthesis

---

## Recommendation for Assessment

**Start Simple, Then Enhance:**

1. **Day 1-4**: Build basic single-agent version (proves it works)
2. **Day 5-6**: Refactor into hybrid (shows architectural skill)
3. **Day 7-8**: Add advanced features (clarification, self-correction)

This progression shows:
- You can deliver (basic version works)
- You can architect (refactor shows design thinking)
- You can innovate (advanced features show creativity)

**Perfect for senior-level demonstration!**
