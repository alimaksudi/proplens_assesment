"""
Lead model for capturing user contact information.
"""

import uuid
from django.db import models
from typing import Dict, Any


class Lead(models.Model):
    """
    Lead information captured during conversation.

    Implements progressive lead capture strategy where information
    is gathered incrementally as user shows more interest.
    """

    LEAD_SOURCE_CHOICES = [
        ('website_chat', 'Website Chat'),
        ('referral', 'Referral'),
        ('direct', 'Direct'),
    ]

    id = models.AutoField(primary_key=True)
    conversation_id = models.UUIDField(db_index=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    lead_source = models.CharField(
        max_length=50,
        choices=LEAD_SOURCE_CHOICES,
        default='website_chat'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leads'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['conversation_id']),
        ]

    def __str__(self) -> str:
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{name or 'Anonymous'} - {self.email or 'No email'}"

    @property
    def full_name(self) -> str:
        """Get full name of lead."""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def is_complete(self) -> bool:
        """Check if lead has all required information for booking."""
        return all([
            self.first_name,
            self.last_name,
            self.email,
        ])

    def to_dict(self) -> Dict[str, Any]:
        """Convert lead to dictionary for API responses."""
        return {
            'id': self.id,
            'conversation_id': str(self.conversation_id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'preferences': self.preferences,
            'lead_source': self.lead_source,
            'is_complete': self.is_complete(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
