from abc import ABC, abstractmethod
import json
from typing import Dict, Any, List

from django.db import models
from pgvector.django import VectorField, HnswIndex


class EmbeddedModel(models.Model, ABC):
    SCHEMA_FIELDS: List[str]
        
    @abstractmethod
    def get_embedding_key(self) -> str:
        pass
    
    def get_schema(self) -> str:
        schema = Dict[str, Any]
        for field in self._meta.get_fields():
            if field.name in self.SCHEMA_FIELDS:
                schema[field.name] = {
                    "field_name": field.name,
                    "field_type": field.get_internal_type(),
                    "field_help_text": field.help_text,
                    "field_required": field.required,
                    "field_default": field.default,
                    "field_choices": field.choices,
                    "field_max_length": field.max_length,
                    "field_null": field.null,
                    "field_blank": field.blank,
                    "field_unique": field.unique,
                }
        return json.dumps(schema, indent=4)
    
    
    class Meta:
        abstract = True
        indexes = [
            HnswIndex(
                name='embedding_index',
                fields=['embedding'],
                opclasses=['vector_cosine_ops'],
            )
        ]


class EmbeddedModelSmall(EmbeddedModel, ABC):
    embedding = VectorField(dimensions=1536)


class EmbeddedModelLarge(EmbeddedModel, ABC):
    embedding = VectorField(dimensions=3072)


class TimedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True