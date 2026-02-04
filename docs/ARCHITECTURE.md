# Silver Land Properties - Architecture Documentation

## System Overview

Silver Land Properties is a conversational AI agent built with Django, LangGraph, and React. The agent helps users find properties, answer questions, and book viewings through natural language conversation.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript + Vite |
| Backend | Django 5.0 + Django Ninja |
| AI Framework | LangGraph + LangChain |
| LLM | OpenAI GPT-4o-mini |
| Database | PostgreSQL 15 |
| Vector Store | ChromaDB (for Vanna SQL) |
| Web Search | Tavily API |
| Container | Docker + Docker Compose |

---

## High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["Frontend (React)"]
        UI[Chat UI]
        API_Client[API Client]
    end

    subgraph Server["Backend (Django)"]
        API[Django Ninja API]
        Controller[Conversation Controller]
        Agent[LangGraph Agent]

        subgraph Nodes["Agent Nodes"]
            Greeting[Greeting]
            Intent[Intent Classifier]
            Discover[Preference Discovery]
            Search[Property Search]
            Recommend[Recommendation]
            QA[Question Answering]
            Booking[Booking Proposal]
            Lead[Lead Capture]
            Confirm[Booking Confirmation]
        end

        subgraph Tools["Agent Tools"]
            Vanna[Vanna SQL Tool]
            BookingTool[Booking Tool]
            Tavily[Tavily Search]
        end
    end

    subgraph Storage["Data Layer"]
        DB[(PostgreSQL)]
        Chroma[(ChromaDB)]
    end

    subgraph External["External Services"]
        OpenAI[OpenAI API]
        TavilyAPI[Tavily API]
    end

    UI --> API_Client
    API_Client --> API
    API --> Controller
    Controller --> Agent
    Agent --> Nodes
    Nodes --> Tools
    Nodes --> OpenAI
    Tools --> DB
    Tools --> Chroma
    Tools --> TavilyAPI
```

---

## LangGraph State Machine - Conversation Flow

```mermaid
stateDiagram-v2
    [*] --> greeting: User opens chat

    greeting --> classify_intent: After greeting

    classify_intent --> discover_preferences: share_preferences / greeting
    classify_intent --> answer_questions: ask_question / clarify / other (with context)
    classify_intent --> search_properties: request_recommendations (with preferences)
    classify_intent --> propose_booking: express_interest / book_viewing
    classify_intent --> capture_lead: provide_contact
    classify_intent --> end_conversation: goodbye
    classify_intent --> discover_preferences: other (no context)

    discover_preferences --> search_properties: preferences_complete
    discover_preferences --> classify_intent: needs more info

    search_properties --> recommend_properties: results found
    search_properties --> discover_preferences: no results

    recommend_properties --> classify_intent: wait for user response

    answer_questions --> classify_intent: answered

    propose_booking --> capture_lead: user wants to book
    propose_booking --> classify_intent: user declines

    capture_lead --> confirm_booking: lead data complete
    capture_lead --> classify_intent: needs more info

    confirm_booking --> [*]: booking created

    end_conversation --> [*]
```

---

## Detailed Node Flow with Routing Logic

```mermaid
flowchart TD
    Start([User Message]) --> Greeting{First Message?}

    Greeting -->|Yes| GreetNode[greeting node]
    Greeting -->|No| Intent[classify_intent node]
    GreetNode --> Intent

    Intent --> Router{Route by Intent}

    Router -->|greeting<br>share_preferences| Discover[discover_preferences]
    Router -->|ask_question<br>clarify| QA[answer_questions]
    Router -->|request_recommendations| CheckPrefs{Has Preferences?}
    Router -->|express_interest<br>book_viewing| Booking[propose_booking]
    Router -->|provide_contact| Lead[capture_lead]
    Router -->|goodbye| End([End])
    Router -->|other| CheckContext{Has Context?}

    CheckPrefs -->|Yes| Search[search_properties]
    CheckPrefs -->|No| Discover

    CheckContext -->|Yes, >2 messages| QA
    CheckContext -->|No| Discover

    Discover --> CheckComplete{Preferences<br>Complete?}
    CheckComplete -->|Yes| Search
    CheckComplete -->|No| WaitUser1([Wait for User])

    Search --> Recommend[recommend_properties]
    Recommend --> WaitUser2([Wait for User])

    QA --> WaitUser3([Wait for User])

    Booking --> Lead
    Lead --> CheckLead{Lead Data<br>Complete?}
    CheckLead -->|Yes| Confirm[confirm_booking]
    CheckLead -->|No| WaitUser4([Wait for User])

    Confirm --> Success([Booking Created])

    WaitUser1 --> Intent
    WaitUser2 --> Intent
    WaitUser3 --> Intent
    WaitUser4 --> Intent
```

---

## Data Models

```mermaid
erDiagram
    Project {
        uuid id PK
        string project_name
        string city
        string country
        int bedrooms
        int bathrooms
        decimal price_usd
        decimal price_local
        string currency
        decimal area_sqm
        string property_type
        string completion_status
        json features
        text description
        string developer
        datetime created_at
        datetime updated_at
    }

    Conversation {
        uuid id PK
        json state
        datetime created_at
        datetime updated_at
    }

    Lead {
        uuid id PK
        uuid conversation_id FK
        string first_name
        string last_name
        string email
        string phone
        json preferences
        datetime created_at
        datetime updated_at
    }

    Booking {
        uuid id PK
        uuid lead_id FK
        uuid project_id FK
        uuid conversation_id FK
        string status
        text notes
        datetime scheduled_date
        datetime created_at
    }

    Lead ||--o{ Booking : "has"
    Project ||--o{ Booking : "has"
    Conversation ||--o| Lead : "creates"
    Conversation ||--o{ Booking : "creates"
```

---

## API Endpoints

```mermaid
flowchart LR
    subgraph API["REST API Endpoints"]
        subgraph Conversations
            POST1[POST /conversations/]
            GET1[GET /conversations/{id}]
        end

        subgraph Agent
            POST2[POST /agents/chat]
        end

        subgraph Health
            GET2[GET /health/]
        end
    end

    Client[Frontend] --> POST1
    Client --> GET1
    Client --> POST2
    Client --> GET2
```

### Endpoint Details

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/conversations/` | Create new conversation |
| GET | `/api/v1/conversations/{id}` | Get conversation state |
| POST | `/api/v1/agents/chat` | Send message to agent |
| GET | `/api/v1/health/` | Health check |

---

## Agent Nodes Description

| Node | Purpose | Triggers |
|------|---------|----------|
| `greeting` | Welcome user, set tone | First message |
| `classify_intent` | Analyze user intent | Every message |
| `discover_preferences` | Extract property preferences | share_preferences, greeting |
| `search_properties` | Query database for matches | preferences complete |
| `recommend_properties` | Present results naturally | search results found |
| `answer_questions` | Answer user queries | ask_question intent |
| `propose_booking` | Initiate viewing booking | express_interest, book_viewing |
| `capture_lead` | Collect user contact info | provide_contact, booking flow |
| `confirm_booking` | Create and confirm booking | lead data complete |

---

## Tool Integration

```mermaid
flowchart TB
    subgraph Tools
        VannaTool[Vanna SQL Tool]
        BookingTool[Booking Tool]
        TavilyTool[Tavily Search Tool]
    end

    subgraph Usage
        Search[search_properties] -->|Fallback SQL| VannaTool
        Lead[capture_lead] -->|Upsert Lead| BookingTool
        Confirm[confirm_booking] -->|Create Booking| BookingTool
        QA[answer_questions] -->|External Info| TavilyTool
    end

    VannaTool -->|Text-to-SQL| DB[(PostgreSQL)]
    BookingTool -->|CRUD| DB
    TavilyTool -->|Web Search| Tavily[Tavily API]
```

---

## State Management (ConversationState)

```mermaid
flowchart LR
    subgraph State["ConversationState TypedDict"]
        messages["messages: List[Dict]"]
        preferences["preferences: Dict"]
        search_results["search_results: List"]
        lead_data["lead_data: Dict"]
        booking_id["booking_id: Optional[str]"]
        current_node["current_node: str"]
        user_intent["user_intent: str"]
        error_message["error_message: Optional[str]"]
        tools_used["tools_used: List[str]"]
    end

    DB[(PostgreSQL)] -->|Load| State
    State -->|Save| DB
    State -->|deepcopy| SafeState[Safe State Copy]
    SafeState -->|Process| Nodes[Agent Nodes]
```

---

## Request Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant G as LangGraph
    participant LLM as OpenAI
    participant DB as PostgreSQL

    U->>F: Type message
    F->>A: POST /agents/chat
    A->>DB: Load conversation state
    A->>G: process_message(state, message)

    G->>G: validate_message()
    G->>G: deepcopy(state)

    G->>LLM: classify_intent
    LLM-->>G: intent

    alt intent = share_preferences
        G->>LLM: discover_preferences
        LLM-->>G: extracted preferences
        G->>DB: search properties
        DB-->>G: results
        G->>LLM: recommend_properties
        LLM-->>G: recommendation text
    else intent = ask_question
        G->>LLM: answer_questions
        opt needs web search
            G->>Tavily: search query
            Tavily-->>G: web results
        end
        LLM-->>G: answer text
    else intent = book_viewing
        G->>LLM: propose_booking
        G->>LLM: capture_lead
        G->>DB: upsert lead
        G->>DB: create booking
        LLM-->>G: confirmation
    end

    G-->>A: updated state
    A->>DB: Save conversation state
    A-->>F: response
    F-->>U: Display message
```

---

## Docker Architecture

```mermaid
flowchart TB
    subgraph Docker["Docker Compose"]
        subgraph Network["proplens_network"]
            FE[silver_land_frontend<br>:3001 -> :5173]
            BE[silver_land_backend<br>:8000]
            DB[silver_land_db<br>:5433 -> :5432]
        end

        subgraph Volumes
            V1[(postgres_data)]
            V2[(chroma_data)]
        end
    end

    FE -->|API calls| BE
    BE -->|SQL| DB
    DB --- V1
    BE --- V2

    User[Browser] -->|:3001| FE
    User -->|:8000| BE
```

---

## File Structure

```
proplens_assesment/
├── backend/
│   ├── src/
│   │   ├── agent/
│   │   │   ├── graph.py           # LangGraph definition
│   │   │   ├── state.py           # ConversationState
│   │   │   ├── nodes/             # All agent nodes
│   │   │   │   ├── greeting.py
│   │   │   │   ├── intent_classifier.py
│   │   │   │   ├── preference_discovery.py
│   │   │   │   ├── property_search.py
│   │   │   │   ├── recommendation.py
│   │   │   │   ├── question_answering.py
│   │   │   │   ├── booking_proposal.py
│   │   │   │   ├── lead_capture.py
│   │   │   │   └── booking_confirmation.py
│   │   │   ├── tools/             # Agent tools
│   │   │   │   ├── vanna_sql_tool.py
│   │   │   │   ├── booking_tool.py
│   │   │   │   └── tavily_search_tool.py
│   │   │   └── schemas.py         # Pydantic validation
│   │   ├── api/
│   │   │   └── controllers/       # API endpoints
│   │   ├── domain/
│   │   │   ├── models.py          # Django models
│   │   │   └── management/        # Import commands
│   │   └── config/
│   │       └── settings.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Chat/
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── App.tsx
│   └── Dockerfile
├── data/
│   └── Property_sales_agent_-_Challenge.csv
├── docker-compose.yml
├── .env
└── ARCHITECTURE.md
```

---

## Environment Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | LLM model to use | gpt-4o-mini |
| `TAVILY_API_KEY` | Tavily search API key | Optional |
| `DB_HOST` | PostgreSQL host | db |
| `DB_PORT` | PostgreSQL port | 5432 |
| `DJANGO_DEBUG` | Debug mode | True |

---

## Key Design Decisions

1. **LangGraph for Orchestration**: Provides state machine with conditional routing, checkpointing, and easy debugging.

2. **Intent Classification First**: Every message goes through intent classification to determine the appropriate node.

3. **Progressive Lead Capture**: Contact info collected incrementally (first name → email → phone) without overwhelming users.

4. **Two-Tier Search**: Django ORM for primary search, Vanna SQL as fallback for complex queries.

5. **Web Search Fallback**: Tavily integration for external information (schools, transport, neighborhood).

6. **Deep Copy State**: Prevents race conditions when multiple requests modify state.

7. **Pydantic Validation**: Input sanitization for security and data integrity.

---

## Running the Application

```bash
# Start all services
docker-compose up -d

# Import property data
docker-compose exec backend sh -c "cd /app/src && python manage.py import_properties /app/data/Property_sales_agent_-_Challenge.csv"

# Access the application
# Frontend: http://localhost:3001
# Backend API: http://localhost:8000/api/v1/
# Health Check: http://localhost:8000/api/v1/health/
```
