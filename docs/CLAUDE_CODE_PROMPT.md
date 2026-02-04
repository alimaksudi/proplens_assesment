# PROMPT FOR CLAUDE CODE
## Silver Land Properties - Conversational AI Agent Implementation

---

## Context

You are implementing a production-grade conversational AI agent for a property sales company. This is an assessment submission that will be evaluated based on:

1. **Architecture quality**: Clean LangGraph design, proper tool orchestration
2. **Code quality**: Modular, well-tested, follows best practices
3. **Business understanding**: Agent drives user towards booking goal
4. **Completeness**: All requirements met with working deployment

**Your role:** Senior AI Engineer implementing this system using Django Ninja, LangGraph, and Vanna AI.

---

## Key Documents Available

1. **PROJECT_DOCUMENTATION.md**: Complete business analysis, architecture decisions, and design rationale
2. **CLAUDE_CODE_GUIDE.md**: Step-by-step implementation instructions organized by phases
3. **Property_sales_agent_-_Challenge.csv**: Property data to import

---

## Core Requirements Summary

### Business Goal
Build a conversational agent that:
- Discovers user's property preferences (city, bedrooms, budget)
- Recommends matching properties from database
- Answers questions about properties
- Drives user to book a property viewing
- Captures lead information (name, email)

### Technical Requirements
- **Framework**: Django Ninja with Ninja Extra (OOP controllers)
- **Agent**: LangGraph for conversation orchestration
- **Text-to-SQL**: Vanna AI with ChromaDB
- **Database**: PostgreSQL (can start with SQLite)
- **LLM**: OpenAI GPT-4o-mini
- **Deployment**: Render or Vercel
- **Testing**: Comprehensive unit and integration tests

### API Endpoints
```
POST /api/v1/conversations - Create new conversation
POST /api/v1/agents/chat - Send message, get response
```

---

## Implementation Strategy

### Phase 1: Foundation (Start Here)
**Deliverables:** Django setup, database models, CSV import, health check

**Critical path:**
1. Create Django project with Ninja API
2. Define models (Project, Lead, Booking, Conversation, SQLTrainingExample)
3. Create migrations and run them
4. Import CSV data into database
5. Create health check endpoint and verify

**Verification:**
- Can run server: `python manage.py runserver`
- Health check works: `curl http://localhost:8000/api/v1/health/`
- Database has properties: Check Django admin

### Phase 2: Agent Core
**Deliverables:** LangGraph state machine, conversation nodes

**Critical path:**
1. Define ConversationState TypedDict
2. Build LangGraph with nodes: greet → classify_intent → discover_preferences → search → recommend → propose_booking → capture_lead → confirm_booking
3. Implement routing logic (conditional edges)
4. Test state transitions with unit tests

**Key decision:** The graph should maintain conversation context and route intelligently based on user intent.

### Phase 3: Tools Integration
**Deliverables:** Vanna Text-to-SQL, booking tool, optional web search

**Critical path:**
1. Setup Vanna with ChromaDB
2. Train Vanna with DDL and 20-30 SQL examples
3. Create VannaSQLTool that takes natural language → SQL → results
4. Create BookingTool that handles lead capture and booking creation
5. Integrate tools into LangGraph nodes

**Key decision:** Vanna should be trained with diverse examples covering: city filters, bedroom filters, price ranges, property types.

### Phase 4: Testing
**Deliverables:** 80%+ code coverage, integration tests

**Critical path:**
1. Unit tests for each node
2. Integration tests for full conversation flows
3. Test edge cases (no matches, invalid input, etc.)

### Phase 5: Deployment
**Deliverables:** Deployed on Render with documentation

**Critical path:**
1. Create Dockerfile (if needed)
2. Configure Render with PostgreSQL
3. Set environment variables
4. Deploy and test live
5. Write README with setup instructions

---

## Critical Implementation Details

### 1. LangGraph State Management
```python
# State must persist across API calls
# Solution: Save state to database after each turn

class ConversationState(TypedDict):
    conversation_id: str
    messages: List[Dict[str, str]]
    preferences: Dict[str, any]
    preferences_complete: bool
    search_results: List[Dict]
    recommended_projects: List[int]
    lead_data: Dict[str, str]
    selected_project_id: Optional[int]
    booking_id: Optional[int]
    # ... more fields
```

### 2. Node Implementation Pattern
```python
async def discover_preferences(state: ConversationState) -> ConversationState:
    """
    Extract user preferences from conversation
    Update state with extracted info
    """
    
    # 1. Get last user message
    last_message = state["messages"][-1]["content"]
    
    # 2. Use LLM to extract structured preferences
    llm = ChatOpenAI(model="gpt-4o-mini")
    extraction_prompt = f"""
    Extract property preferences from: "{last_message}"
    Return JSON: {{"city": str, "bedrooms": int, "budget_max": int}}
    """
    
    # 3. Parse and update state
    extracted = llm.invoke(extraction_prompt)
    state["preferences"].update(extracted)
    
    # 4. Check if we have enough info
    state["preferences_complete"] = all([
        state["preferences"].get("city"),
        state["preferences"].get("bedrooms") or state["preferences"].get("budget_max")
    ])
    
    # 5. Generate response
    if not state["preferences_complete"]:
        response = "Great! What's your budget range?"
    else:
        response = "Perfect! Let me find matching properties..."
    
    state["messages"].append({"role": "assistant", "content": response})
    
    return state
```

### 3. Vanna SQL Tool Usage
```python
# In search_properties node:

from agent.tools.vanna_sql_tool import get_vanna_tool

async def search_properties(state: ConversationState) -> ConversationState:
    vanna = get_vanna_tool()
    
    # Build natural language query from preferences
    prefs = state["preferences"]
    query = f"Find {prefs['bedrooms']}-bedroom properties in {prefs['city']}"
    
    if prefs.get("budget_max"):
        query += f" under ${prefs['budget_max']}"
    
    # Execute query
    results = await vanna.query_properties(query)
    
    # Store results in state
    state["search_results"] = results
    state["recommended_projects"] = [r["id"] for r in results[:3]]
    
    return state
```

### 4. API Controller Structure
```python
from ninja_extra import api_controller, http_post
from api.schemas.request import ChatRequest
from api.schemas.response import ChatResponse
from agent.graph import PropertyAgentGraph

@api_controller('/agents', tags=['Agent'])
class ConversationController:
    
    def __init__(self):
        self.agent_graph = PropertyAgentGraph(llm=ChatOpenAI())
    
    @http_post('/chat', response=ChatResponse)
    async def chat(self, request: ChatRequest):
        """
        Process user message and return agent response
        """
        
        # 1. Load existing conversation state from DB
        conversation = Conversation.objects.filter(
            id=request.conversation_id
        ).first()
        
        existing_state = conversation.state if conversation else None
        
        # 2. Process message through agent graph
        updated_state = await self.agent_graph.process_message(
            conversation_id=request.conversation_id,
            message=request.message,
            existing_state=existing_state
        )
        
        # 3. Save updated state
        Conversation.objects.update_or_create(
            id=request.conversation_id,
            defaults={"state": updated_state}
        )
        
        # 4. Format response
        return ChatResponse(
            conversation_id=request.conversation_id,
            response={
                "message": updated_state["messages"][-1]["content"],
                "recommendations": self._format_recommendations(updated_state),
                "state": updated_state["current_node"]
            }
        )
```

---

## Common Pitfalls to Avoid

### 1. ❌ Hallucinating Property Details
**Problem:** LLM invents property features not in database
**Solution:** 
- Always use Vanna to query database
- Validate all property data against database
- Explicitly tell LLM: "Only use information from the provided search results"

### 2. ❌ Losing Conversation Context
**Problem:** Agent forgets previous preferences
**Solution:**
- Save state to database after each turn
- Load state before processing new message
- Pass full message history to LLM when needed

### 3. ❌ Poor SQL Generation
**Problem:** Vanna generates incorrect SQL
**Solution:**
- Train with 30+ diverse examples
- Include examples for edge cases (NULL values, JSONB queries)
- Log generated SQL for debugging
- Add fallback: if query returns 0 results, try broader search

### 4. ❌ Premature Booking Request
**Problem:** Agent asks for contact info too early
**Solution:**
- Only propose booking after user shows interest
- Look for keywords: "interested", "like this", "tell me more"
- Progressive lead capture: preferences first, contact info last

### 5. ❌ Infinite Loops in Graph
**Problem:** Graph cycles indefinitely between nodes
**Solution:**
- Add retry counters to state
- Set maximum iterations (e.g., max 20 nodes per conversation turn)
- Always have END condition in conditional edges

---

## Testing Checklist

### Unit Tests
- [ ] Each node function works in isolation
- [ ] Preference extraction from various phrasings
- [ ] SQL generation for common queries
- [ ] Booking tool creates correct database records

### Integration Tests
- [ ] Full conversation: greet → discover → recommend → book
- [ ] No exact match scenario (cross-sell logic)
- [ ] User asks question mid-conversation
- [ ] User abandons, then resumes conversation

### Edge Cases
- [ ] Empty search results (no matching properties)
- [ ] User provides incomplete contact info
- [ ] Database connection fails (graceful error)
- [ ] LLM API timeout (retry logic)

---

## Deployment Checklist

### Before Deploying
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations run successfully
- [ ] CSV data imported
- [ ] Vanna trained with SQL examples
- [ ] Health check endpoint returns 200

### On Render
- [ ] Create PostgreSQL service
- [ ] Create Web Service (Django app)
- [ ] Set environment variables:
  - `DATABASE_URL`
  - `OPENAI_API_KEY`
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG=False`
  - `ALLOWED_HOSTS`
  - `CHROMA_PERSIST_DIR`
- [ ] Deploy and verify
- [ ] Test live endpoint: POST to `/api/v1/agents/chat`

---

## Example Conversation Flow to Test

```
1. User: "Hi, I'm looking for a 2-bedroom apartment"
   Agent: "Welcome! I'd be happy to help. What city are you interested in?"

2. User: "Chicago"
   Agent: "Great choice! What's your budget range?"

3. User: "Around $800k to $1 million"
   Agent: "Perfect! I found 3 excellent options. Here's the top match:
          The Residences at St. Regis Chicago
          - $850,000
          - 2 bed, 2 bath
          - 318 sqm
          - Features: Rooftop pool, 24hr concierge..."

4. User: "Tell me more about the location"
   Agent: "The St. Regis is in the prestigious Lakeshore East neighborhood.
          Within walking distance: Millennium Park (0.5 mi), Navy Pier (0.8 mi)..."

5. User: "I'd like to schedule a viewing"
   Agent: "Excellent! To book your viewing, what's your first name?"

6. User: "John"
   Agent: "Thanks, John! And your last name?"

7. User: "Smith"
   Agent: "Perfect. What's the best email to send confirmation?"

8. User: "john.smith@email.com"
   Agent: "Wonderful! I've scheduled your viewing.
          Confirmation sent to john.smith@email.com.
          Our team will contact you within 24 hours."
```

---

## File Structure Reference

```
silver-land-properties/
├── src/
│   ├── config/
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # API routes
│   │   └── wsgi.py
│   ├── api/
│   │   ├── controllers/
│   │   │   ├── conversation_controller.py  # Main API endpoint
│   │   │   └── health_controller.py
│   │   ├── schemas/
│   │   │   ├── request.py       # Pydantic request models
│   │   │   └── response.py      # Pydantic response models
│   │   └── middleware/
│   ├── agent/
│   │   ├── graph.py             # LangGraph orchestrator
│   │   ├── state.py             # ConversationState definition
│   │   ├── nodes/               # Individual conversation nodes
│   │   │   ├── greeting.py
│   │   │   ├── intent_classifier.py
│   │   │   ├── preference_discovery.py
│   │   │   ├── property_search.py
│   │   │   ├── recommendation.py
│   │   │   ├── question_answering.py
│   │   │   ├── booking_proposal.py
│   │   │   ├── lead_capture.py
│   │   │   ├── booking_confirmation.py
│   │   │   └── error_handler.py
│   │   └── tools/               # Agent tools
│   │       ├── vanna_sql_tool.py
│   │       ├── booking_tool.py
│   │       └── web_search_tool.py (optional)
│   ├── domain/
│   │   ├── models.py            # Django ORM models
│   │   ├── admin.py             # Django admin config
│   │   └── management/
│   │       └── commands/
│   │           └── import_properties.py  # CSV import command
│   └── manage.py
├── tests/
│   ├── unit/
│   │   ├── test_nodes.py
│   │   ├── test_tools.py
│   │   └── test_models.py
│   ├── integration/
│   │   └── test_conversation_flow.py
│   └── fixtures/
│       └── sample_conversations.json
├── docs/
│   ├── PROJECT_DOCUMENTATION.md
│   ├── CLAUDE_CODE_GUIDE.md
│   └── API.md
├── .env
├── .gitignore
├── requirements.txt
├── Dockerfile (optional)
├── docker-compose.yml (optional)
└── README.md
```

---

## Success Criteria

Your implementation is successful when:

✅ **Functional**
- [ ] Agent completes full flow: greet → discover → search → recommend → book
- [ ] Text-to-SQL works for 80%+ of queries
- [ ] No hallucinated property details
- [ ] Bookings saved correctly to database

✅ **Code Quality**
- [ ] Clean architecture (separation of concerns)
- [ ] Type hints on all functions
- [ ] Comprehensive docstrings
- [ ] 80%+ test coverage
- [ ] Follows PEP 8 style

✅ **Deployed**
- [ ] Running on Render (or Vercel)
- [ ] API accessible via public URL
- [ ] Response times < 2 seconds
- [ ] No errors in logs

✅ **Documented**
- [ ] README with clear setup instructions
- [ ] API documentation (Swagger auto-generated)
- [ ] Architecture decision records

---

## Getting Started Command

```bash
# 1. Read the project documentation
cat PROJECT_DOCUMENTATION.md | head -n 100

# 2. Follow the implementation guide
cat CLAUDE_CODE_GUIDE.md | head -n 200

# 3. Start with Phase 1: Foundation
mkdir silver-land-properties && cd silver-land-properties
python -m venv venv && source venv/bin/activate
pip install django django-ninja django-ninja-extra
django-admin startproject config src/

# 4. Continue with setup as per CLAUDE_CODE_GUIDE.md
```

---

## Key Questions to Ask During Implementation

1. **State Persistence**: How should I save/load conversation state between API calls?
   → Store in Conversation model as JSONB

2. **Error Handling**: What if Vanna generates invalid SQL?
   → Log error, return empty results, ask user to rephrase

3. **No Matches**: What if search returns 0 properties?
   → Cross-sell: "No exact matches, but here are similar options..."
   → Suggest adjusting criteria: "Would you like to expand your budget?"

4. **Incomplete Lead**: What if user stops mid-booking?
   → Save partial lead data (progressive capture)
   → Resume if they return

5. **Testing Strategy**: How deep should tests be?
   → Unit tests: 60% (each node, each tool)
   → Integration tests: 30% (full flows)
   → Performance tests: 10% (response time)

---

## Final Notes

- **Focus on clarity**: Code should be readable by other senior engineers
- **Document decisions**: Why LangGraph? Why GPT-4o-mini? (see PROJECT_DOCUMENTATION.md)
- **Test thoroughly**: This demonstrates engineering maturity
- **Deploy early**: Don't wait until end; deploy after Phase 2 to catch issues

**Remember:** This is assessed as a Lead/Senior AI Engineer role. Show architectural thinking, not just coding ability.

Good luck! 🚀
