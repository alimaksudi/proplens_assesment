"""
Health check controller for API monitoring.
"""

from ninja_extra import api_controller, http_get
from ninja import Schema
from django.db import connection
from domain.models import Project


class HealthResponse(Schema):
    """Health check response schema."""
    status: str
    database: str
    version: str
    project_count: int


@api_controller('/health', tags=['Health'])
class HealthController:
    """Health check endpoint for monitoring and deployment verification."""

    @http_get('/', response=HealthResponse)
    def check_health(self):
        """
        Health check endpoint.

        Returns the API status, database connectivity, and basic statistics.
        """
        db_status = "connected"
        project_count = 0

        try:
            connection.ensure_connection()
            project_count = Project.objects.count()
        except Exception:
            db_status = "disconnected"

        return {
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0",
            "project_count": project_count,
        }
