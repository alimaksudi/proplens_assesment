"""
Project model representing property listings.
"""

from django.db import models
from typing import Dict, List, Any


class Project(models.Model):
    """
    Property project entity representing individual listings.

    Contains all property details including location, specifications,
    pricing, and metadata for data quality tracking.
    """

    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
    ]

    COMPLETION_STATUS_CHOICES = [
        ('available', 'Available'),
        ('off_plan', 'Off Plan'),
        ('under_construction', 'Under Construction'),
        ('completed', 'Completed'),
    ]

    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255, db_index=True)
    developer_name = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=2)
    property_type = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPE_CHOICES,
        null=True,
        blank=True
    )
    bedrooms = models.IntegerField(null=True, blank=True, db_index=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    price_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True
    )
    area_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    unit_type = models.CharField(max_length=100, null=True, blank=True)
    completion_status = models.CharField(
        max_length=50,
        choices=COMPLETION_STATUS_CHOICES,
        null=True,
        blank=True
    )
    completion_date = models.DateField(null=True, blank=True)
    features = models.JSONField(default=list, blank=True)
    facilities = models.JSONField(default=list, blank=True)
    description = models.TextField(null=True, blank=True)

    # Data quality tracking
    data_source = models.CharField(max_length=50, default='csv_import')
    import_batch_id = models.CharField(max_length=50, null=True, blank=True)
    data_quality_score = models.FloatField(default=1.0)
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list, blank=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        indexes = [
            models.Index(fields=['city', 'bedrooms', 'price_usd']),
            models.Index(fields=['is_valid']),
            models.Index(fields=['property_type']),
        ]

    def __str__(self) -> str:
        return f"{self.project_name} - {self.city}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for API responses."""
        return {
            'id': self.id,
            'project_name': self.project_name,
            'developer_name': self.developer_name,
            'city': self.city,
            'country': self.country,
            'property_type': self.property_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'price_usd': float(self.price_usd) if self.price_usd else None,
            'area_sqm': float(self.area_sqm) if self.area_sqm else None,
            'unit_type': self.unit_type,
            'completion_status': self.completion_status,
            'completion_date': str(self.completion_date) if self.completion_date else None,
            'features': self.features,
            'facilities': self.facilities,
            'description': self.description[:500] if self.description else None,
        }

    def get_key_features(self, limit: int = 5) -> List[str]:
        """Get a limited list of key features for display."""
        features = self.features or []
        facilities = self.facilities or []
        combined = features + facilities
        return combined[:limit] if combined else []
