# Implementation Instructions: Silver Land Properties Conversational AI Agent

## Project Overview

You are implementing a production-grade conversational AI agent for Silver Land Properties, a real estate company. The system guides property buyers from initial inquiry through property discovery to booking a viewing appointment.

This is an assessment for a Lead AI Engineer position. The solution must demonstrate senior-level engineering through clean architecture, comprehensive testing, and production-ready implementation.

## Documentation Structure

All detailed guidance is available in the docs folder:

### Core Documentation
- PROJECT_DOCUMENTATION.md - Complete technical design and architecture decisions
- CLAUDE_CODE_GUIDE.md - Detailed phase-by-phase implementation instructions
- BUSINESS_CLARIFICATIONS.md - Business logic and strategic decisions
- AGENT_ARCHITECTURE.md - Agent design patterns and tool architecture
- DATA_PIPELINE.md - CSV import and data quality pipeline
- README_TEMPLATE.md - Final project documentation template
- QUICK_START_GUIDE.md - Quick reference and answers to key questions

### Reference Materials
- Property_sales_agent_-_Challenge.csv - Dataset with 17,318 property records

Refer to these documents for detailed implementation guidance, code patterns, and design decisions.

## Technology Stack

### Backend
- Framework: Django 5.0 with Django Ninja and Ninja Extra
- Agent Orchestration: LangGraph 0.0.40
- Language Models: OpenAI GPT-4o-mini
- Text-to-SQL: Vanna AI with ChromaDB
- Database: PostgreSQL 14+
- Testing: pytest with pytest-django
- Deployment: Render

### Frontend (Monorepo Structure)
- Framework: React 18 with TypeScript
- Build Tool: Vite 5
- UI Components: Assistant UI library
- Styling: Tailwind CSS
- Deployment: Vercel

### Project Structure (Monorepo)
```
silver-land-properties/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   ├── api/
│   │   ├── agent/
│   │   └── domain/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   └── pages/
│   └── package.json
├── docs/
└── data/
```

## Core Requirements

### Business Objectives
1. Discover user property preferences through natural conversation
2. Search and recommend matching properties from database
3. Answer questions about properties using database and web search
4. Guide users toward booking a property viewing
5. Capture lead information for sales team follow-up

### Technical Requirements
1. RESTful API with two primary endpoints: conversation creation and message handling
2. LangGraph-based conversational state machine with proper flow control
3. Text-to-SQL capability using Vanna AI for natural language property queries
4. Conversation state persistence across multiple API calls
5. Lead and booking management with database persistence
6. Comprehensive testing with 80%+ code coverage
7. Production deployment with proper monitoring

### User Experience Requirements
1. Modern chat interface using Assistant UI components
2. Real-time conversation with sub-2-second response times
3. Visual property cards displaying recommendations
4. Progressive lead capture without overwhelming users
5. Clear error handling and loading states

## Architecture Overview

### Agent Design Pattern
Implement a hybrid architecture with a single LangGraph orchestrator managing conversation flow, delegating to specialized tool-agents for domain-specific tasks.

Main Orchestrator responsibilities:
- Conversation flow management
- Intent classification
- State persistence
- Response generation

Tool-Agent responsibilities:
- Property search with fuzzy matching
- Question answering with context
- Booking management with validation
- Query clarification when needed

### Database Schema
Four core tables with proper relationships:
- Projects: Property listings with comprehensive metadata
- Leads: User contact information and preferences
- Bookings: Property viewing appointments
- Conversations: LangGraph state checkpoints for persistence

Additional considerations:
- Data quality scoring for imported records
- Audit trails for all user actions
- Unique constraints to prevent duplicates
- Indexes on frequently queried fields

### API Design
Follow REST principles with clear separation of concerns:
- Conversation lifecycle management
- Stateless message processing with server-side state storage
- Structured JSON responses with metadata
- Proper HTTP status codes and error handling

## Implementation Phases

### Phase 1: Backend Foundation (Days 1-2)
Objective: Establish working Django API with database and data import

Key Deliverables:
- Django project with Ninja API configuration
- Database models with migrations
- Enhanced CSV import command with validation
- Health check endpoint
- Basic API documentation

Verification Criteria:
- Server runs without errors
- Database migrations apply successfully
- CSV data imports with quality reports
- API documentation accessible at /docs endpoint

### Phase 2: Agent Core (Days 3-4)
Objective: Build LangGraph state machine with conversation nodes

Key Deliverables:
- ConversationState type definition
- LangGraph state machine with conditional routing
- Core conversation nodes implementation
- State persistence mechanism
- Basic conversation controller

Verification Criteria:
- State machine handles basic conversation flow
- State persists correctly between API calls
- Conversation context maintained across turns
- Unit tests for individual nodes pass

### Phase 3: Tool Integration (Days 5-6)
Objective: Integrate Vanna SQL and booking capabilities

Key Deliverables:
- Vanna AI setup with ChromaDB
- SQL training with schema and examples
- Tool-agent implementations
- Property search with fuzzy matching
- Booking creation with validation

Verification Criteria:
- Natural language queries generate correct SQL
- Search returns relevant properties
- No exact match triggers fuzzy search
- Bookings persist to database correctly

### Phase 4: Frontend Development (Days 7-8)
Objective: Build modern chat interface with Assistant UI

Key Deliverables:
- Vite project setup with React and TypeScript
- Assistant UI integration
- Chat interface components
- Property display cards
- API client with error handling
- Loading and error states

Verification Criteria:
- Chat interface renders correctly
- Messages send and receive properly
- Property recommendations display in UI
- Error states handle gracefully
- Responsive design works on mobile

### Phase 5: Testing (Days 9)
Objective: Comprehensive testing coverage

Key Deliverables:
- Unit tests for all components
- Integration tests for complete flows
- Performance tests for response times
- Frontend component tests
- Test coverage reports

Verification Criteria:
- 80%+ backend code coverage
- All integration tests pass
- Response times under 2 seconds
- Frontend components render correctly

### Phase 6: Deployment (Day 10)
Objective: Production deployment with monitoring

Key Deliverables:
- Backend deployed to Render
- Frontend deployed to Vercel
- Environment configuration
- Database migrations on production
- Final documentation

Verification Criteria:
- Health check passes on live URL
- Full conversation flow works end-to-end
- No errors in production logs
- Documentation complete and accurate

## Critical Implementation Guidelines

### Code Quality Standards
- Use type hints throughout Python codebase
- Write comprehensive docstrings for all functions and classes
- Follow PEP 8 style guidelines
- Implement proper error handling with informative messages
- Use dependency injection for testability
- Keep functions focused with single responsibilities

### Architecture Principles
- Separation of concerns between layers
- Dependency inversion for flexibility
- Interface-based design for tool-agents
- State management through explicit state objects
- Immutability where appropriate

### Testing Strategy
- Test individual components in isolation
- Mock external dependencies in unit tests
- Use real integrations in integration tests
- Test error conditions and edge cases
- Verify state transitions in conversation flow

### Security Considerations
- Never log sensitive user information
- Validate all user inputs
- Use parameterized queries for SQL
- Implement rate limiting on API endpoints
- Secure environment variable management
- HTTPS enforcement in production

### Performance Optimization
- Database query optimization with proper indexes
- Batch processing for CSV imports
- Caching for frequently accessed data
- Lazy loading for frontend components
- Response streaming where applicable

## Key Business Logic

### Lead Capture Strategy
Implement progressive lead capture to maximize conversion:
- Early stage: Collect preferences only
- Engagement stage: Show recommendations and answer questions
- Commitment stage: Capture contact information only when booking intent is clear

### Property Matching Logic
Three-tier matching approach:
- Exact match: All criteria met within stated ranges
- Close match: One parameter off by 20% or less, with transparency
- Alternative: Different location or adjusted criteria, with explanation

Never show non-matches without explicit disclosure.

### Conversation Context Management
Weighted recency system for preference tracking:
- Recent messages (last 3): Highest weight for current intent
- Medium history (4-10 messages): Context for understanding
- Older messages (11+): Background information only

Explicit overrides always take precedence over implicit preferences.

### Query Clarification
Detect and handle ambiguous queries:
- Missing essential information triggers clarifying questions
- Contradictory statements prompt confirmation
- Vague criteria lead to helpful suggestions

### Web Search Boundaries
Invoke external search only for:
- Project-specific factual queries (nearby schools, transportation)
- Amenities not present in database
- Neighborhood information

Never use web search for:
- General property recommendations (must use database)
- Pricing or availability (database is source of truth)
- Legal or financial advice (decline politely)

## Frontend Implementation Guidelines

### Assistant UI Integration
- Follow Assistant UI documentation for chat components
- Implement proper message threading
- Handle loading states during API calls
- Display typing indicators for better UX
- Support message history scrolling

### Property Display
- Create reusable property card components
- Show relevant property details clearly
- Implement image galleries where applicable
- Display pricing and key features prominently
- Include call-to-action buttons

### State Management
- Use React hooks for local state
- Implement proper error boundaries
- Handle API errors gracefully
- Persist conversation ID across page refreshes
- Clear state on conversation reset

### Responsive Design
- Mobile-first approach with Tailwind
- Touch-friendly interaction targets
- Readable typography across devices
- Optimized images for performance
- Progressive enhancement strategy

## Data Quality and Import

### CSV Import Pipeline
Implement robust ETL process:
- Extract with encoding detection
- Transform with validation and normalization
- Load in batches with transaction safety
- Validate post-import with quality reports

### Data Validation
- Type checking for all fields
- Range validation for numeric values
- Format validation for dates and text
- Business rule enforcement
- Quality scoring based on completeness

### Error Handling
- Log all import errors with row numbers
- Continue processing after individual failures
- Generate comprehensive error reports
- Support dry-run mode for preview

## Success Metrics

### Functional Completeness
- Full conversation flow from greeting to booking
- Accurate property search with relevant results
- Proper lead and booking persistence
- Conversation memory across sessions
- Error recovery and graceful degradation

### Code Quality Metrics
- 80%+ test coverage
- Zero critical security vulnerabilities
- Clean separation of concerns
- Comprehensive documentation
- Proper error handling throughout

### Performance Targets
- API response time under 2 seconds (95th percentile)
- SQL query execution under 500ms
- Frontend initial load under 3 seconds
- Conversation state retrieval under 100ms

### User Experience Quality
- Intuitive conversation flow
- Clear property recommendations
- Helpful error messages
- Responsive interface across devices
- Professional visual design

## Deployment Configuration

### Backend (Render)
- PostgreSQL managed database service
- Web service for Django application
- Environment variables properly configured
- Database migrations automated
- Logging and monitoring enabled

### Frontend (Vercel)
- Static site deployment
- Environment variables for API endpoints
- Custom domain configuration
- CDN for asset delivery
- Analytics integration

### Environment Management
Separate configurations for:
- Development: Debug enabled, verbose logging
- Staging: Production-like with test data
- Production: Optimized, monitored, secured

## Documentation Requirements

### Code Documentation
- Inline comments for complex logic
- Docstrings following Google style
- Type hints throughout
- README with setup instructions
- API documentation auto-generated

### Architecture Documentation
- System design diagrams
- Database schema documentation
- API contract specifications
- Deployment procedures
- Troubleshooting guides

### User Documentation
- API usage examples
- Frontend integration guide
- Environment setup instructions
- Common issues and solutions

## Final Notes

This implementation demonstrates senior-level engineering through:
- Clear architectural decisions with documented rationale
- Production-ready code with comprehensive testing
- Proper separation of concerns across layers
- Thoughtful user experience design
- Complete documentation for maintainability

Focus on delivering a system that works reliably, scales appropriately, and can be maintained by other engineers. Quality over quantity in all aspects.

Refer to the detailed documentation in the docs folder for specific implementation patterns, code examples, and design decisions. Each phase has comprehensive guidance to ensure successful implementation.

The goal is not just to meet requirements, but to demonstrate the engineering judgment, technical expertise, and professional craftsmanship expected of a Lead AI Engineer.
