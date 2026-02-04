"""
URL configuration for Silver Land Properties API.
"""

from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from api.controllers.health_controller import HealthController
from api.controllers.conversation_controller import ConversationController, AgentController

api = NinjaExtraAPI(
    title="Silver Land Properties API",
    version="1.0.0",
    description="Conversational AI Agent for Property Sales"
)

api.register_controllers(
    HealthController,
    ConversationController,
    AgentController,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
]
