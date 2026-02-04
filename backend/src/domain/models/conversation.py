"""
Conversation model for LangGraph state persistence.
"""

import uuid
from django.db import models
from typing import Dict, Any, Optional


class Conversation(models.Model):
    """
    Conversation state storage for LangGraph checkpointing.

    Stores the complete state of a conversation including messages,
    user preferences, and agent state for resumption.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.JSONField(default=dict, blank=True)
    last_activity = models.DateTimeField(auto_now=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversations'
        indexes = [
            models.Index(fields=['last_activity']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"Conversation {self.id}"

    def get_messages(self) -> list:
        """Get message history from state."""
        return self.state.get('messages', [])

    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences from state."""
        return self.state.get('preferences', {})

    def get_current_node(self) -> str:
        """Get current conversation node."""
        return self.state.get('current_node', 'greeting')

    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update conversation state."""
        self.state = new_state
        self.save()

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for API responses."""
        return {
            'id': str(self.id),
            'current_node': self.get_current_node(),
            'message_count': len(self.get_messages()),
            'preferences': self.get_preferences(),
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
