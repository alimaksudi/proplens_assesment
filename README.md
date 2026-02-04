# Silver Land Properties - Conversational AI Agent

A production-grade conversational AI agent for property sales, built with Django Ninja, LangGraph, and React.

## Overview

This application provides a modern chat interface for property buyers to discover properties, ask questions, and book viewings. The AI agent uses natural language processing to understand user preferences and recommend matching properties from a database of 17,000+ listings.

## Features

- Natural conversation flow for property discovery
- Intelligent property search and matching
- Progressive lead capture
- Property viewing booking system
- Responsive chat interface with property cards
- Production-ready architecture

## Project Structure

```
proplens_assesment/
├── backend/                 # Django backend
│   ├── src/
│   │   ├── config/         # Django settings
│   │   ├── api/            # REST controllers
│   │   ├── agent/          # LangGraph agent
│   │   └── domain/         # Models and services
│   ├── tests/              # Backend tests
│   ├── requirements.txt
│   └── render.yaml         # Render deployment
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── lib/            # Utilities
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── vercel.json         # Vercel deployment
│
├── data/                   # CSV data files
│   └── Property_sales_agent_-_Challenge.csv
│
└── docs/                   # Documentation
    ├── IMPLEMENTATION_PROMPT.md
    ├── PROJECT_DOCUMENTATION.md
    ├── CLAUDE_CODE_GUIDE.md
    └── ...
```

## Technology Stack

### Backend
- Django 5.0 with Django Ninja API
- LangGraph for conversation orchestration
- OpenAI GPT-4o-mini for language understanding
- Vanna AI with ChromaDB for Text-to-SQL
- PostgreSQL database

### Frontend
- React 18 with TypeScript
- Vite build tool
- Tailwind CSS styling
- Custom chat components

## Getting Started

### Quick Start with Docker (Recommended)

The easiest way to run the application is with Docker:

```bash
# 1. Clone and navigate to project
cd proplens_assesment

# 2. Create environment file
cp .env.example .env
# Edit .env with your OpenAI API key (required) and Tavily key (optional)

# 3. Start all services
docker-compose up -d

# 4. Import property data (first time only)
docker-compose exec backend sh -c "cd /app/src && python manage.py import_properties /app/data/Property_sales_agent_-_Challenge.csv"

# 5. Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/api/v1/
```

**Docker Services:**
- `db` - PostgreSQL 15 database (port 5432)
- `backend` - Django API server (port 8000)
- `frontend` - React dev server (port 5173)

**Useful Docker Commands:**
```bash
# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run backend tests
docker-compose exec backend sh -c "cd /app && pytest"

# Access Django shell
docker-compose exec backend sh -c "cd /app/src && python manage.py shell"
```

---

### Manual Setup (Alternative)

#### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- OpenAI API key

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Create database
createdb silver_land_db

# Run migrations
cd src
python manage.py migrate

# Import property data
python manage.py import_properties ../../data/Property_sales_agent_-_Challenge.csv

# Create admin user (optional)
python manage.py createsuperuser

# Run server
python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit with API endpoint

# Run development server
npm run dev
```

#### Running Tests

Backend:
```bash
cd backend
pytest --cov=src
```

Frontend:
```bash
cd frontend
npm test
```

## API Endpoints

### Health Check
```
GET /api/v1/health/
```

### Create Conversation
```
POST /api/v1/conversations/
```

### Send Message
```
POST /api/v1/agents/chat
Content-Type: application/json

{
  "conversation_id": "uuid",
  "message": "I'm looking for a 2-bedroom apartment in Chicago"
}
```

## Deployment

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your repository
3. Set environment variables
4. Deploy

### Frontend (Vercel)

1. Import project to Vercel
2. Configure build settings
3. Set environment variables
4. Deploy

## Environment Variables

### Backend
- `DJANGO_SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key (required)
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)
- `TAVILY_API_KEY` - Tavily API key for web search (optional)
- `CORS_ALLOWED_ORIGINS` - Frontend URL

### Frontend
- `VITE_API_BASE_URL` - Backend API URL

## Architecture

The system uses a hybrid agent architecture with:
- Single LangGraph orchestrator for conversation flow
- Specialized tool-agents for property search, booking, and Q&A
- Progressive lead capture strategy
- State persistence across API calls

## Documentation

For detailed implementation guidance, see the `/docs` folder:
- `IMPLEMENTATION_PROMPT.md` - Main implementation instructions
- `PROJECT_DOCUMENTATION.md` - Complete technical design
- `CLAUDE_CODE_GUIDE.md` - Phase-by-phase implementation guide
- `AGENT_ARCHITECTURE.md` - Agent design patterns
- `FRONTEND_GUIDE.md` - React implementation guide

## License

This project is for assessment purposes only.

## Author

Built as a technical assessment for Lead AI Engineer role.
