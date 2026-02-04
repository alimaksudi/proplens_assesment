"""
Django admin configuration for domain models.
"""

from django.contrib import admin
from .models import Project, Lead, Booking, Conversation, SQLTrainingExample


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'project_name',
        'city',
        'bedrooms',
        'price_usd',
        'completion_status',
        'data_quality_score',
        'is_valid'
    ]
    list_filter = ['city', 'bedrooms', 'property_type', 'is_valid', 'completion_status']
    search_fields = ['project_name', 'city', 'developer_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'data_quality_score', 'validation_errors']
    ordering = ['-created_at']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'email',
        'phone',
        'lead_source',
        'created_at'
    ]
    list_filter = ['lead_source', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'conversation_id']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'lead', 'project', 'status', 'booking_date', 'visit_date']
    list_filter = ['status', 'booking_date']
    search_fields = ['lead__email', 'project__project_name']
    readonly_fields = ['created_at', 'updated_at', 'conversation_id']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_activity', 'created_at']
    list_filter = ['created_at', 'last_activity']
    readonly_fields = ['id', 'created_at', 'last_activity']


@admin.register(SQLTrainingExample)
class SQLTrainingExampleAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question', 'sql_query']
