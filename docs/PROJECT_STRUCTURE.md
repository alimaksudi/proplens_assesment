# Project Structure: Monorepo Organization

## Overview

This document outlines the recommended monorepo structure for the Silver Land Properties conversational AI agent, combining backend and frontend in a unified repository.

## Root Directory Structure

```
silver-land-properties/
├── backend/                 # Django backend application
├── frontend/                # React frontend application
├── docs/                    # Project documentation
├── data/                    # Data files and seeds
├── .gitignore
├── README.md
└── docker-compose.yml       # Optional: Local development setup
```

## Backend Directory Structure

```
backend/
├── src/
│   ├── config/             # Django project configuration
│   │   ├── __init__.py
│   │   ├── settings.py     # Django settings
│   │   ├── urls.py         # URL routing
│   │   ├── wsgi.py         # WSGI application
│   │   └── asgi.py         # ASGI application
│   │
│   ├── api/                # REST API layer
│   │   ├── __init__.py
│   │   ├── controllers/    # API controllers
│   │   │   ├── __init__.py
│   │   │   ├── conversation_controller.py
│   │   │   └── health_controller.py
│   │   ├── schemas/        # Request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── request.py
│   │   │   └── response.py
│   │   └── middleware/     # Custom middleware
│   │       └── __init__.py
│   │
│   ├── agent/              # LangGraph agent implementation
│   │   ├── __init__.py
│   │   ├── graph.py        # Main orchestrator
│   │   ├── state.py        # State definition
│   │   ├── nodes/          # Conversation nodes
│   │   │   ├── __init__.py
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
│   │   └── tools/          # Agent tools
│   │       ├── __init__.py
│   │       ├── vanna_sql_tool.py
│   │       ├── booking_tool.py
│   │       └── web_search_tool.py
│   │
│   ├── domain/             # Domain layer
│   │   ├── __init__.py
│   │   ├── models.py       # Django ORM models
│   │   ├── admin.py        # Django admin configuration
│   │   ├── services/       # Business logic services
│   │   │   └── __init__.py
│   │   └── management/     # Django management commands
│   │       └── commands/
│   │           ├── __init__.py
│   │           ├── import_properties_v2.py
│   │           └── data_quality_report.py
│   │
│   └── manage.py           # Django management script
│
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── unit/              # Unit tests
│   │   ├── __init__.py
│   │   ├── test_nodes.py
│   │   ├── test_tools.py
│   │   └── test_models.py
│   ├── integration/       # Integration tests
│   │   ├── __init__.py
│   │   └── test_conversation_flow.py
│   └── fixtures/          # Test data
│       └── sample_conversations.json
│
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── pytest.ini             # Pytest configuration
├── .env.example           # Environment variables template
└── README.md              # Backend-specific documentation
```

## Frontend Directory Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── property/
│   │   │   ├── PropertyCard.tsx
│   │   │   ├── PropertyList.tsx
│   │   │   └── PropertyDetails.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Layout.tsx
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       └── Loading.tsx
│   │
│   ├── lib/               # Utilities and helpers
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── types.ts
│   │   └── utils/
│   │       ├── formatters.ts
│   │       └── validators.ts
│   │
│   ├── hooks/             # Custom React hooks
│   │   ├── useConversation.ts
│   │   ├── useProperties.ts
│   │   └── useApi.ts
│   │
│   ├── pages/             # Page components
│   │   ├── Home.tsx
│   │   └── NotFound.tsx
│   │
│   ├── types/             # TypeScript type definitions
│   │   ├── conversation.ts
│   │   ├── property.ts
│   │   └── api.ts
│   │
│   ├── styles/            # Global styles
│   │   └── globals.css
│   │
│   ├── App.tsx            # Main application component
│   └── main.tsx           # Application entry point
│
├── public/                # Static assets
│   ├── favicon.ico
│   └── images/
│
├── index.html             # HTML template
├── package.json           # Node dependencies
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── .env.example           # Environment variables template
└── README.md              # Frontend-specific documentation
```

## Documentation Directory Structure

```
docs/
├── PROJECT_DOCUMENTATION.md        # Complete technical design
├── CLAUDE_CODE_GUIDE.md            # Implementation guide
├── BUSINESS_CLARIFICATIONS.md      # Business logic
├── AGENT_ARCHITECTURE.md           # Agent design
├── DATA_PIPELINE.md                # CSV import guide
├── FRONTEND_GUIDE.md               # Frontend implementation
├── README_TEMPLATE.md              # Final README template
├── QUICK_START_GUIDE.md            # Quick reference
└── IMPLEMENTATION_PROMPT.md        # Main prompt file
```

## Data Directory Structure

```
data/
├── Property_sales_agent_-_Challenge.csv    # Source data
├── seed/                                    # Seed data for development
│   ├── projects.json
│   └── test_conversations.json
└── exports/                                 # Data exports
```

## Key Organization Principles

### Separation of Concerns
Backend and frontend are clearly separated at the root level. Each has its own dependencies and configuration. Shared concerns are documented in the docs folder.

### Layer Architecture
Backend follows layered architecture with clear boundaries:
- API layer handles HTTP concerns
- Agent layer manages conversation logic
- Domain layer contains business entities and rules

### Component Hierarchy
Frontend components are organized by feature and type:
- Feature folders group related components
- Common components are shared across features
- Hooks encapsulate reusable logic

### Configuration Management
Each environment has appropriate configuration:
- Development: Local settings with debugging enabled
- Staging: Production-like for testing
- Production: Optimized and secured

### Test Organization
Tests mirror source structure for easy navigation:
- Unit tests focus on individual components
- Integration tests verify component interactions
- Fixtures provide reusable test data

## File Naming Conventions

### Backend Python Files
- snake_case for all Python files
- Descriptive names indicating purpose
- Prefixes for special files (test_, command_)

### Frontend TypeScript Files
- PascalCase for component files
- camelCase for utility and hook files
- .tsx extension for components with JSX
- .ts extension for pure TypeScript

### Configuration Files
- Follow tool conventions (package.json, tsconfig.json)
- Use descriptive names for custom configs
- Include .example suffix for templates

## Development Workflow

### Backend Development
Navigate to backend directory. Activate virtual environment. Run Django development server. Make changes and test locally.

### Frontend Development
Navigate to frontend directory. Install dependencies with package manager. Run Vite development server. Changes hot-reload automatically.

### Full Stack Development
Run both backend and frontend servers. Frontend proxies API requests to backend. Test integration between layers. Deploy both together.

## Deployment Structure

### Backend Deployment
Deploy to Render or similar platform. Connect to managed PostgreSQL database. Set environment variables appropriately. Run migrations on deployment.

### Frontend Deployment
Deploy to Vercel or similar platform. Configure API endpoint environment variable. Enable CDN for static assets. Set up automatic deployments.

### Monorepo Deployment
Backend and frontend can deploy independently. Each has its own deployment pipeline. Coordinate versions for compatibility. Use semantic versioning.

## Environment Variables

### Backend Variables
Database connection strings. API keys for external services. Django configuration settings. Feature flags and toggles.

### Frontend Variables
Backend API endpoint URL. Analytics tracking IDs. Feature flags for UI. Build-time configuration.

### Shared Variables
Environment name (dev, staging, prod). Logging configuration. Monitoring service credentials.

## Documentation Maintenance

### Code Documentation
Keep inline comments current with code changes. Update docstrings when signatures change. Document complex logic thoroughly. Maintain API documentation accuracy.

### Project Documentation
Review docs folder regularly. Update as architecture evolves. Keep setup instructions current. Document breaking changes.

### Architecture Decision Records
Document significant decisions. Explain rationale and alternatives. Track changes over time. Reference in code where relevant.

## Git Workflow

### Branch Strategy
Main branch for production code. Development branch for integration. Feature branches for new work. Release branches for deployments.

### Commit Conventions
Use descriptive commit messages. Follow conventional commits format. Reference issues in commits. Keep commits focused and atomic.

### Code Review
Review all changes before merging. Check tests and documentation. Verify no secrets committed. Ensure CI passes.

## Conclusion

This monorepo structure provides clear organization while maintaining separation between backend and frontend concerns. The structure scales well as the project grows and makes it easy for developers to navigate the codebase.

Follow these organizational principles consistently to maintain code quality and developer productivity throughout the project lifecycle.
