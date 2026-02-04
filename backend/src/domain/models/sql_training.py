"""
SQL Training model for Vanna Text-to-SQL training examples.
"""

from django.db import models
from typing import Dict, Any


class SQLTrainingExample(models.Model):
    """
    Training examples for Vanna Text-to-SQL model.

    Stores question-SQL pairs used to train the Vanna model
    for accurate natural language to SQL conversion.
    """

    id = models.AutoField(primary_key=True)
    question = models.TextField()
    sql_query = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sql_training_examples'

    def __str__(self) -> str:
        return f"SQL Example: {self.question[:50]}..."

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'question': self.question,
            'sql_query': self.sql_query,
            'is_active': self.is_active,
        }
