# CLAUDE CODE IMPLEMENTATION GUIDE
## Silver Land Properties - Conversational AI Agent

---

## Overview

This guide provides step-by-step instructions for Claude Code to implement the Silver Land Properties conversational AI agent. Follow the phases sequentially for best results.

**Total Implementation Time:** ~56 hours across 10 days
**Primary Technologies:** Django Ninja, LangGraph, Vanna AI, PostgreSQL, OpenAI GPT-4o-mini

---

## Pre-Implementation Setup

### 1. Create Project Structure
```bash
mkdir silver-land-properties
cd silver-land-properties

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create directory structure
mkdir -p src/{api/{controllers,schemas,middleware},agent/{nodes,tools},domain/{models,services},config,database/{migrations,seeds}}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p docs
```

### 2. Initialize Git Repository
```bash
git init
git add .gitignore README.md
git commit -m "Initial commit: project structure"
```

### 3. Install Dependencies
Create `requirements.txt`:
```txt
# Core Framework
django>=5.0.0
django-ninja>=1.1.0
django-ninja-extra>=0.20.0
gunicorn>=21.2.0
python-dotenv>=1.0.0

# Database
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.25

# Agent & LLM
langgraph>=0.0.40
langchain>=0.1.0
langchain-openai>=0.0.5
openai>=1.12.0

# Text-to-SQL
vanna>=0.3.4
chromadb>=0.4.22

# Web Search (optional)
tavily-python>=0.3.0  # or duckduckgo-search

# Utilities
pydantic>=2.5.0
pydantic-settings>=2.1.0
httpx>=0.26.0
redis>=5.0.1

# Testing
pytest>=7.4.0
pytest-django>=4.7.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
factory-boy>=3.3.0
faker>=22.0.0

# Development
black>=24.0.0
ruff>=0.1.0
mypy>=1.8.0
ipython>=8.20.0
```

Install:
```bash
pip install -r requirements.txt
```

---

## PHASE 1: Foundation (Days 1-2)

### Task 1.1: Django Project Setup

**Goal:** Create Django project with Ninja API configured

**Steps:**
1. Create Django project:
```bash
django-admin startproject config src/
cd src
python manage.py startapp api
python manage.py startapp agent
python manage.py startapp domain
```

2. Configure `src/config/settings.py`:
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ninja_extra',
    'api',
    'agent',
    'domain',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'silver_land_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Vanna Configuration
CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', str(BASE_DIR / 'chroma_db'))

# LangGraph Configuration
LANGGRAPH_CHECKPOINT_DIR = os.getenv('LANGGRAPH_CHECKPOINT_DIR', str(BASE_DIR / 'checkpoints'))

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

3. Create `src/config/urls.py`:
```python
from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from api.controllers.conversation_controller import ConversationController
from api.controllers.health_controller import HealthController

api = NinjaExtraAPI(
    title="Silver Land Properties API",
    version="1.0.0",
    description="Conversational AI Agent for Property Sales"
)

api.register_controllers(
    HealthController,
    ConversationController,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
]
```

4. Create `.env` file:
```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=silver_land_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Vanna
CHROMA_PERSIST_DIR=./chroma_db

# LangGraph
LANGGRAPH_CHECKPOINT_DIR=./checkpoints
```

**Verification:**
```bash
python manage.py runserver
# Visit http://localhost:8000/api/v1/docs - should see Swagger UI
```

### Task 1.2: Database Models

**Goal:** Define SQLAlchemy/Django models for projects, leads, bookings, conversations

**File:** `src/domain/models.py`
```python
from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid

class Project(models.Model):
    """Property project entity"""
    
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    developer_name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=2)
    property_type = models.CharField(max_length=50)  # apartment, villa
    bedrooms = models.IntegerField(null=True, blank=True, db_index=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    price_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, db_index=True)
    area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completion_status = models.CharField(max_length=50, null=True, blank=True)  # off_plan, x_available
    completion_date = models.DateField(null=True, blank=True)
    features = models.JSONField(default=list, blank=True)  # List of features
    facilities = models.JSONField(default=list, blank=True)  # List of facilities
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['price_usd']),
            models.Index(fields=['bedrooms']),
        ]
    
    def __str__(self):
        return f"{self.project_name} - {self.city}"


class Lead(models.Model):
    """Lead information captured during conversation"""
    
    id = models.AutoField(primary_key=True)
    conversation_id = models.UUIDField(db_index=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True)  # {city, budget_min, budget_max, bedrooms}
    lead_source = models.CharField(max_length=50, default='website_chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leads'
        unique_together = [['conversation_id', 'email']]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class Booking(models.Model):
    """Property viewing bookings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='bookings')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bookings')
    conversation_id = models.UUIDField(db_index=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    visit_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookings'
    
    def __str__(self):
        return f"Booking #{self.id} - {self.project.project_name}"


class Conversation(models.Model):
    """Conversation state for LangGraph checkpointing"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.JSONField(default=dict, blank=True)  # LangGraph checkpoint
    last_activity = models.DateTimeField(auto_now=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversations'
        indexes = [
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Conversation {self.id}"


class SQLTrainingExample(models.Model):
    """Training examples for Vanna Text-to-SQL"""
    
    id = models.AutoField(primary_key=True)
    question = models.TextField()
    sql_query = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sql_training_examples'
    
    def __str__(self):
        return f"SQL Example: {self.question[:50]}"
```

**Steps:**
1. Create migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

2. Create Django admin interface (`src/domain/admin.py`):
```python
from django.contrib import admin
from .models import Project, Lead, Booking, Conversation, SQLTrainingExample

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'city', 'bedrooms', 'price_usd', 'completion_status']
    list_filter = ['city', 'bedrooms', 'property_type']
    search_fields = ['project_name', 'city', 'developer_name']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'conversation_id', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'lead', 'project', 'status', 'booking_date']
    list_filter = ['status']

admin.site.register(Conversation)
admin.site.register(SQLTrainingExample)
```

3. Create superuser:
```bash
python manage.py createsuperuser
```

### Task 1.3: CSV Data Import

**Goal:** Load property data from CSV into PostgreSQL

**File:** `src/domain/management/commands/import_properties.py`
```python
import csv
import json
from django.core.management.base import BaseCommand
from domain.models import Project
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import properties from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
    
    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        self.stdout.write(self.style.SUCCESS(f'Importing from {csv_file_path}...'))
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            imported_count = 0
            
            for row in reader:
                try:
                    # Parse completion date
                    completion_date = None
                    if row.get('completion_date'):
                        try:
                            completion_date = datetime.strptime(
                                row['completion_date'], '%d-%m-%Y'
                            ).date()
                        except ValueError:
                            pass
                    
                    # Parse features and facilities (from JSON string)
                    features = []
                    facilities = []
                    if row.get('features'):
                        try:
                            features = json.loads(row['features'])
                        except json.JSONDecodeError:
                            features = []
                    
                    if row.get('facilities'):
                        try:
                            facilities = json.loads(row['facilities'])
                        except json.JSONDecodeError:
                            facilities = []
                    
                    # Create or update project
                    project, created = Project.objects.update_or_create(
                        project_name=row['Project name'],
                        city=row['city'],
                        defaults={
                            'developer_name': row.get('developer name', ''),
                            'country': row.get('country', ''),
                            'property_type': row.get('Property type (apartment/villa)', 'apartment'),
                            'bedrooms': int(row['No of bedrooms']) if row.get('No of bedrooms') else None,
                            'bathrooms': int(row['bathrooms']) if row.get('bathrooms') else None,
                            'price_usd': Decimal(row['Price (USD)']) if row.get('Price (USD)') else None,
                            'area_sqm': Decimal(row['Area (sq mtrs)']) if row.get('Area (sq mtrs)') else None,
                            'completion_status': row.get('Completion status (off plan/available)', ''),
                            'completion_date': completion_date,
                            'features': features,
                            'facilities': facilities,
                            'description': row.get('Project description', ''),
                        }
                    )
                    
                    if created:
                        imported_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error importing row: {e}')
                    )
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {imported_count} properties')
        )
```

**Run import:**
```bash
# Copy CSV to project directory first
python manage.py import_properties /path/to/Property_sales_agent_-_Challenge.csv
```

### Task 1.4: Health Check Endpoint

**Goal:** Create basic health check to verify API is running

**File:** `src/api/controllers/health_controller.py`
```python
from ninja_extra import api_controller, http_get
from ninja import Schema
from django.db import connection

class HealthResponse(Schema):
    status: str
    database: str
    version: str

@api_controller('/health', tags=['Health'])
class HealthController:
    
    @http_get('/', response=HealthResponse)
    def check_health(self):
        """Health check endpoint"""
        
        # Check database connection
        db_status = "connected"
        try:
            connection.ensure_connection()
        except Exception:
            db_status = "disconnected"
        
        return {
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0"
        }
```

**Verification:**
```bash
curl http://localhost:8000/api/v1/health/
# Expected: {"status":"healthy","database":"connected","version":"1.0.0"}
```

---

## PHASE 2: Agent Core (Days 3-4)

### Task 2.1: Define Conversation State

**File:** `src/agent/state.py`
```python
from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime

class ConversationState(TypedDict):
    """State object for LangGraph conversation flow"""
    
    # Conversation metadata
    conversation_id: str
    current_node: str
    
    # Message history
    messages: List[Dict[str, str]]  # [{"role": "user/assistant", "content": "..."}]
    
    # User preferences
    preferences: Dict[str, any]  # {city, bedrooms, budget_min, budget_max, property_type}
    preferences_complete: bool
    
    # Search results
    search_results: List[Dict]  # List of matching properties
    recommended_projects: List[int]  # Project IDs
    
    # Lead information (progressive capture)
    lead_data: Dict[str, str]  # {first_name, last_name, email, phone}
    lead_captured: bool
    
    # Booking information
    selected_project_id: Optional[int]
    booking_id: Optional[int]
    booking_confirmed: bool
    
    # Intent tracking
    user_intent: Optional[Literal[
        "greeting",
        "share_preferences",
        "ask_question",
        "request_recommendations",
        "express_interest",
        "book_viewing",
        "provide_contact",
        "other"
    ]]
    
    # Error handling
    error_message: Optional[str]
    retry_count: int
    
    # Metadata
    created_at: datetime
    last_updated: datetime
```

### Task 2.2: LangGraph State Machine

**File:** `src/agent/graph.py`
```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Dict, Literal
import json

from agent.state import ConversationState
from agent.nodes import (
    greet_user,
    classify_intent,
    discover_preferences,
    search_properties,
    recommend_properties,
    answer_questions,
    propose_booking,
    capture_lead_details,
    confirm_booking,
    handle_error
)

class PropertyAgentGraph:
    """LangGraph orchestrator for conversational property agent"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the conversation flow graph"""
        
        graph = StateGraph(ConversationState)
        
        # Add nodes (conversation steps)
        graph.add_node("greet", greet_user)
        graph.add_node("classify_intent", classify_intent)
        graph.add_node("discover_preferences", discover_preferences)
        graph.add_node("search_properties", search_properties)
        graph.add_node("recommend_properties", recommend_properties)
        graph.add_node("answer_questions", answer_questions)
        graph.add_node("propose_booking", propose_booking)
        graph.add_node("capture_lead", capture_lead_details)
        graph.add_node("confirm_booking", confirm_booking)
        graph.add_node("handle_error", handle_error)
        
        # Set entry point
        graph.set_entry_point("greet")
        
        # Add edges (conversation flow)
        graph.add_edge("greet", "classify_intent")
        
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
                END: END
            }
        )
        
        # From discover_preferences
        graph.add_conditional_edges(
            "discover_preferences",
            self._should_search_properties,
            {
                True: "search_properties",
                False: "classify_intent"  # need more info
            }
        )
        
        # From search_properties
        graph.add_edge("search_properties", "recommend_properties")
        
        # From recommend_properties
        graph.add_conditional_edges(
            "recommend_properties",
            self._after_recommendation,
            {
                "propose_booking": "propose_booking",
                "more_questions": "classify_intent",
                END: END
            }
        )
        
        # From answer_questions
        graph.add_conditional_edges(
            "answer_questions",
            self._after_question,
            {
                "propose_booking": "propose_booking",
                "search_again": "search_properties",
                "more_questions": "classify_intent",
                END: END
            }
        )
        
        # From propose_booking
        graph.add_edge("propose_booking", "capture_lead")
        
        # From capture_lead
        graph.add_conditional_edges(
            "capture_lead",
            self._lead_capture_complete,
            {
                True: "confirm_booking",
                False: "capture_lead"  # need more details
            }
        )
        
        # From confirm_booking
        graph.add_edge("confirm_booking", END)
        
        # From handle_error
        graph.add_edge("handle_error", "classify_intent")
        
        return graph
    
    def _route_after_classification(self, state: ConversationState) -> str:
        """Route conversation based on classified intent"""
        intent = state.get("user_intent", "other")
        
        if intent == "greeting":
            return "discover"
        elif intent == "share_preferences":
            return "discover"
        elif intent == "ask_question":
            return "question"
        elif intent == "request_recommendations":
            if state.get("preferences_complete"):
                return "search"
            else:
                return "discover"
        elif intent == "express_interest":
            return "recommend"
        elif intent == "book_viewing":
            return "booking"
        elif intent == "provide_contact":
            return "provide_contact"
        else:
            return "discover"
    
    def _should_search_properties(self, state: ConversationState) -> bool:
        """Determine if we have enough preferences to search"""
        prefs = state.get("preferences", {})
        
        # Minimum: city and either bedrooms or budget
        has_city = bool(prefs.get("city"))
        has_bedrooms = prefs.get("bedrooms") is not None
        has_budget = prefs.get("budget_max") is not None
        
        return has_city and (has_bedrooms or has_budget)
    
    def _after_recommendation(self, state: ConversationState) -> str:
        """Decide next step after showing recommendations"""
        # If user shows interest (in their last message), propose booking
        last_message = state["messages"][-1]["content"].lower() if state["messages"] else ""
        
        interest_keywords = ["interested", "like this", "book", "viewing", "schedule", "yes"]
        if any(keyword in last_message for keyword in interest_keywords):
            return "propose_booking"
        
        question_keywords = ["what", "how", "when", "where", "tell me", "?"]
        if any(keyword in last_message for keyword in question_keywords):
            return "more_questions"
        
        return END
    
    def _after_question(self, state: ConversationState) -> str:
        """Decide next step after answering a question"""
        last_message = state["messages"][-1]["content"].lower() if state["messages"] else ""
        
        if "book" in last_message or "schedule" in last_message:
            return "propose_booking"
        elif "show me" in last_message or "other options" in last_message:
            return "search_again"
        
        return "more_questions"
    
    def _lead_capture_complete(self, state: ConversationState) -> bool:
        """Check if we have all required lead information"""
        lead = state.get("lead_data", {})
        
        required_fields = ["first_name", "last_name", "email"]
        return all(lead.get(field) for field in required_fields)
    
    async def process_message(
        self, 
        conversation_id: str, 
        message: str, 
        existing_state: Optional[ConversationState] = None
    ) -> ConversationState:
        """
        Process a user message through the graph
        
        Args:
            conversation_id: Unique conversation identifier
            message: User's message text
            existing_state: Previous conversation state (if resuming)
        
        Returns:
            Updated conversation state
        """
        # Initialize or update state
        if existing_state:
            state = existing_state
            state["messages"].append({"role": "user", "content": message})
        else:
            state = self._initialize_state(conversation_id, message)
        
        # Run the graph
        result = await self.compiled_graph.ainvoke(state)
        
        return result
    
    def _initialize_state(self, conversation_id: str, first_message: str) -> ConversationState:
        """Initialize a new conversation state"""
        from datetime import datetime
        
        return {
            "conversation_id": conversation_id,
            "current_node": "greet",
            "messages": [{"role": "user", "content": first_message}],
            "preferences": {},
            "preferences_complete": False,
            "search_results": [],
            "recommended_projects": [],
            "lead_data": {},
            "lead_captured": False,
            "selected_project_id": None,
            "booking_id": None,
            "booking_confirmed": False,
            "user_intent": None,
            "error_message": None,
            "retry_count": 0,
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
```

### Task 2.3: Implement Core Nodes

**File:** `src/agent/nodes/__init__.py`
```python
from .greeting import greet_user
from .intent_classifier import classify_intent
from .preference_discovery import discover_preferences
from .property_search import search_properties
from .recommendation import recommend_properties
from .question_answering import answer_questions
from .booking_proposal import propose_booking
from .lead_capture import capture_lead_details
from .booking_confirmation import confirm_booking
from .error_handler import handle_error

__all__ = [
    'greet_user',
    'classify_intent',
    'discover_preferences',
    'search_properties',
    'recommend_properties',
    'answer_questions',
    'propose_booking',
    'capture_lead_details',
    'confirm_booking',
    'handle_error',
]
```

**File:** `src/agent/nodes/greeting.py`
```python
from agent.state import ConversationState
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

async def greet_user(state: ConversationState) -> ConversationState:
    """
    Greet the user and set welcoming tone
    Only called on first message in conversation
    """
    
    # Check if this is truly the first interaction
    if len(state["messages"]) > 1:
        # Skip greeting, already in conversation
        return state
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    greeting_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly property sales assistant for Silver Land Properties.
        Your goal is to help buyers find their perfect property and book a viewing.
        
        Generate a warm, concise greeting that:
        1. Welcomes the user
        2. Briefly introduces yourself
        3. Asks how you can help them today
        
        Keep it under 3 sentences. Be natural and conversational."""),
        ("user", "The user just opened the chat. Generate a greeting.")
    ])
    
    chain = greeting_prompt | llm
    response = await chain.ainvoke({})
    
    # Add assistant's greeting to messages
    state["messages"].append({
        "role": "assistant",
        "content": response.content
    })
    
    state["current_node"] = "greet"
    
    return state
```

**Continue with other nodes in similar fashion...** (See detailed implementations in subsequent tasks)

---

## PHASE 3: Tools Integration (Days 5-6)

### Task 3.1: Vanna Text-to-SQL Tool

**File:** `src/agent/tools/vanna_sql_tool.py`
```python
import os
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VannaSQLTool(ChromaDB_VectorStore, OpenAI_Chat):
    """
    Text-to-SQL tool using Vanna AI with ChromaDB for training data storage
    """
    
    def __init__(self, config: Dict[str, Any]):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
        
        self.db_connection_string = os.getenv('DATABASE_URL')
        self._setup_connection()
        self._train_if_needed()
    
    def _setup_connection(self):
        """Setup PostgreSQL connection"""
        try:
            self.connect_to_postgres(
                host=os.getenv('DB_HOST', 'localhost'),
                dbname=os.getenv('DB_NAME', 'silver_land_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                port=int(os.getenv('DB_PORT', 5432))
            )
            logger.info("Vanna connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect Vanna to database: {e}")
            raise
    
    def _train_if_needed(self):
        """Train Vanna with DDL and example queries if not already trained"""
        
        # Check if already trained (in production, check a flag in DB or file)
        # For now, we'll train on every initialization
        
        # 1. Train with DDL
        ddl_statements = [
            """
            CREATE TABLE projects (
                id SERIAL PRIMARY KEY,
                project_name VARCHAR(255) NOT NULL,
                developer_name VARCHAR(255),
                city VARCHAR(100) NOT NULL,
                country VARCHAR(2) NOT NULL,
                property_type VARCHAR(50),
                bedrooms INTEGER,
                bathrooms INTEGER,
                price_usd DECIMAL(12, 2),
                area_sqm DECIMAL(10, 2),
                completion_status VARCHAR(50),
                completion_date DATE,
                features JSONB,
                facilities JSONB,
                description TEXT
            );
            """
        ]
        
        for ddl in ddl_statements:
            try:
                self.train(ddl=ddl)
                logger.info("Trained Vanna with DDL")
            except Exception as e:
                logger.warning(f"DDL training failed (may already exist): {e}")
        
        # 2. Train with example question-SQL pairs
        training_examples = self._get_training_examples()
        
        for example in training_examples:
            try:
                self.train(
                    question=example["question"],
                    sql=example["sql"]
                )
                logger.info(f"Trained example: {example['question'][:50]}...")
            except Exception as e:
                logger.warning(f"Training example failed: {e}")
    
    def _get_training_examples(self) -> List[Dict[str, str]]:
        """Get SQL training examples"""
        
        return [
            {
                "question": "Show me 2-bedroom apartments in Chicago",
                "sql": "SELECT * FROM projects WHERE bedrooms = 2 AND city = 'Chicago' AND property_type = 'apartment' ORDER BY price_usd"
            },
            {
                "question": "What properties are under $1 million?",
                "sql": "SELECT * FROM projects WHERE price_usd < 1000000 ORDER BY price_usd"
            },
            {
                "question": "Find 3-bedroom properties in Chicago under $2 million",
                "sql": "SELECT * FROM projects WHERE bedrooms = 3 AND city = 'Chicago' AND price_usd < 2000000"
            },
            {
                "question": "Show me available properties (not off-plan)",
                "sql": "SELECT * FROM projects WHERE completion_status = 'x_available'"
            },
            {
                "question": "What apartments are in the US?",
                "sql": "SELECT * FROM projects WHERE country = 'US' AND property_type = 'apartment'"
            },
            {
                "question": "Show me villas under $5 million",
                "sql": "SELECT * FROM projects WHERE property_type = 'villa' AND price_usd < 5000000"
            },
            {
                "question": "What are the cheapest 1-bedroom apartments?",
                "sql": "SELECT * FROM projects WHERE bedrooms = 1 AND property_type = 'apartment' ORDER BY price_usd LIMIT 10"
            },
            {
                "question": "Find properties in Singapore",
                "sql": "SELECT * FROM projects WHERE city = 'Singapore' OR country = 'SG'"
            },
            {
                "question": "Show me properties with pools",
                "sql": "SELECT * FROM projects WHERE facilities @> '[\"pool\"]' OR facilities @> '[\"swimming pool\"]'"
            },
            {
                "question": "What 2-bedroom apartments in Chicago are between $500k and $1M?",
                "sql": "SELECT * FROM projects WHERE bedrooms = 2 AND city = 'Chicago' AND price_usd BETWEEN 500000 AND 1000000"
            },
            # Add 20 more examples for comprehensive training...
        ]
    
    async def query_properties(self, natural_language_query: str) -> List[Dict]:
        """
        Convert natural language to SQL and execute query
        
        Args:
            natural_language_query: User's search criteria in natural language
        
        Returns:
            List of matching properties as dictionaries
        """
        try:
            # Generate SQL
            sql = self.generate_sql(natural_language_query)
            logger.info(f"Generated SQL: {sql}")
            
            # Execute SQL
            results = self.run_sql(sql)
            
            # Convert to list of dicts
            if hasattr(results, 'to_dict'):
                # Pandas DataFrame
                return results.to_dict('records')
            elif isinstance(results, list):
                return results
            else:
                return []
        
        except Exception as e:
            logger.error(f"Vanna query failed: {e}")
            return []
    
    async def explain_sql(self, natural_language_query: str) -> str:
        """
        Generate SQL and get explanation (useful for debugging)
        """
        try:
            sql = self.generate_sql(natural_language_query)
            explanation = f"For '{natural_language_query}', I would execute:\n\n{sql}"
            return explanation
        except Exception as e:
            return f"Failed to generate SQL: {e}"


# Singleton instance
_vanna_instance = None

def get_vanna_tool() -> VannaSQLTool:
    """Get or create Vanna tool instance"""
    global _vanna_instance
    
    if _vanna_instance is None:
        config = {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-4o-mini',
            'path': os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
        }
        _vanna_instance = VannaSQLTool(config=config)
    
    return _vanna_instance
```

**Verification:**
```python
# Test script: test_vanna.py
import asyncio
from agent.tools.vanna_sql_tool import get_vanna_tool

async def test_vanna():
    vanna = get_vanna_tool()
    
    queries = [
        "Show me 2-bedroom apartments in Chicago",
        "What properties are under $1 million?",
        "Find available 3-bedroom units"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = await vanna.query_properties(query)
        print(f"Found {len(results)} results")
        if results:
            print(f"Sample: {results[0]['project_name']}")

if __name__ == "__main__":
    asyncio.run(test_vanna())
```

### Task 3.2: Booking Tool

**File:** `src/agent/tools/booking_tool.py`
```python
from domain.models import Lead, Booking, Project
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BookingTool:
    """
    Handle lead capture and booking creation
    """
    
    async def upsert_lead(
        self, 
        conversation_id: str, 
        lead_data: Dict[str, str],
        preferences: Dict[str, any]
    ) -> Lead:
        """
        Create or update lead information
        
        Args:
            conversation_id: Unique conversation ID
            lead_data: {first_name, last_name, email, phone}
            preferences: {city, bedrooms, budget_min, budget_max}
        
        Returns:
            Lead object
        """
        try:
            lead, created = Lead.objects.update_or_create(
                conversation_id=conversation_id,
                email=lead_data.get('email'),
                defaults={
                    'first_name': lead_data.get('first_name'),
                    'last_name': lead_data.get('last_name'),
                    'phone': lead_data.get('phone'),
                    'preferences': preferences,
                    'lead_source': 'website_chat'
                }
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"{action} lead: {lead.email}")
            
            return lead
        
        except Exception as e:
            logger.error(f"Failed to upsert lead: {e}")
            raise
    
    async def create_booking(
        self,
        lead_id: int,
        project_id: int,
        conversation_id: str,
        notes: Optional[str] = None
    ) -> Booking:
        """
        Create a property viewing booking
        
        Args:
            lead_id: Lead database ID
            project_id: Project database ID
            conversation_id: Unique conversation ID
            notes: Optional booking notes
        
        Returns:
            Booking object
        """
        try:
            # Verify project exists
            project = Project.objects.get(id=project_id)
            
            # Create booking
            booking = Booking.objects.create(
                lead_id=lead_id,
                project_id=project_id,
                conversation_id=conversation_id,
                status='pending',
                notes=notes
            )
            
            logger.info(f"Created booking #{booking.id} for project {project.project_name}")
            
            return booking
        
        except Project.DoesNotExist:
            logger.error(f"Project {project_id} not found")
            raise ValueError(f"Invalid project ID: {project_id}")
        
        except Exception as e:
            logger.error(f"Failed to create booking: {e}")
            raise
    
    async def get_booking_confirmation_message(self, booking: Booking) -> str:
        """
        Generate booking confirmation message
        
        Args:
            booking: Booking object
        
        Returns:
            Confirmation message string
        """
        project = booking.project
        lead = booking.lead
        
        message = f"""
Perfect! I've scheduled your viewing for {project.project_name}.

Booking Details:
- Property: {project.project_name}
- Location: {project.city}, {project.country}
- Confirmation sent to: {lead.email}

Our team will contact you within 24 hours to confirm the date and time of your viewing.

Is there anything else I can help you with?
        """.strip()
        
        return message


# Singleton instance
_booking_tool_instance = None

def get_booking_tool() -> BookingTool:
    """Get or create booking tool instance"""
    global _booking_tool_instance
    
    if _booking_tool_instance is None:
        _booking_tool_instance = BookingTool()
    
    return _booking_tool_instance
```

---

## Continue with remaining phases (Phase 4-5) in next response...

This guide provides the foundation. Should I continue with:
- Phase 4: Testing implementation
- Phase 5: Deployment configuration
- Sample node implementations (discover_preferences, search_properties, etc.)
- API schemas and controller implementations
