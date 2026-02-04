"""
Booking model for property viewing appointments.
"""

import uuid
from django.db import models
from typing import Dict, Any


class Booking(models.Model):
    """
    Property viewing booking entity.

    Tracks booking requests from leads for specific properties,
    including status and any notes from the conversation.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    id = models.AutoField(primary_key=True)
    lead = models.ForeignKey(
        'domain.Lead',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    project = models.ForeignKey(
        'domain.Project',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    conversation_id = models.UUIDField(db_index=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    visit_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'visit_bookings'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['conversation_id']),
        ]

    def __str__(self) -> str:
        return f"Booking #{self.id} - {self.project.project_name}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert booking to dictionary for API responses."""
        return {
            'id': self.id,
            'conversation_id': str(self.conversation_id),
            'status': self.status,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'visit_date': str(self.visit_date) if self.visit_date else None,
            'notes': self.notes,
            'lead': {
                'id': self.lead.id,
                'name': self.lead.full_name,
                'email': self.lead.email,
            },
            'project': {
                'id': self.project.id,
                'name': self.project.project_name,
                'city': self.project.city,
                'price_usd': float(self.project.price_usd) if self.project.price_usd else None,
            },
        }
