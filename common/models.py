from __future__ import annotations
from abc import abstractmethod
import json
from typing import Any, Dict, List, Type

from django.db import models
from django.conf import settings
from pgvector.django import VectorField, HnswIndex
from pydantic import BaseModel
from openai import OpenAI


class EmbeddedModelMixin(models.Model):
    SCHEMA_FIELDS: List[str]
    ModelBaseModel: Type[BaseModel]

    @classmethod
    def get_schema(cls) -> str:
        schema = dict()
        for field in cls._meta.get_fields():
            if field.name in cls.SCHEMA_FIELDS:
                schema[field.name] = {
                    "field_name": field.name,
                    "field_type": field.get_internal_type(),
                    "field_help_text": field.help_text,
                    "field_default": str(field.default),
                    "field_choices": field.choices,
                    "field_max_length": field.max_length,
                    "field_null": field.null,
                    "field_unique": field.unique,
                }
        return json.dumps(schema, indent=4)

    @abstractmethod
    def get_embedding_key(self) -> str:
        pass

    @abstractmethod
    def get_embedding(self) -> List[float]:
        pass

    @classmethod
    @abstractmethod
    def create_from_schema(cls, base_model: ModelBaseModel):
        pass

    def save(self, *args, **kwargs):
        self.embedding = self.get_embedding()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
        indexes = [
            HnswIndex(
                name="embedding_index",
                fields=["embedding"],
                opclasses=["vector_cosine_ops"],
            )
        ]


class EmbeddedModelSmallMixin(EmbeddedModelMixin):
    embedding = VectorField(dimensions=1536, null=True)

    def get_embedding(self) -> List[float]:
        client = OpenAI(**settings.LLM_SETTINGS["default"])
        return (
            client.embeddings.create(input=self.get_embedding_key(), model="text-embedding-3-small").data[0].embedding
        )

    class Meta:
        abstract = True


class EmbeddedModelLargeMixin(EmbeddedModelMixin):
    embedding = VectorField(dimensions=3072, null=True)

    def get_embedding(self) -> List[float]:
        client = OpenAI(**settings.LLM_SETTINGS["default"])
        return (
            client.embeddings.create(input=self.get_embedding_key(), model="text-embedding-3-large").data[0].embedding
        )

    class Meta:
        abstract = True


class TimedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AIGeneratableMixin(models.Model):
    raw_data = models.JSONField(null=True, blank=True)
    ai_summary = models.TextField(null=True, blank=True)
    ModelBaseModel: Type[BaseModel]

    @classmethod
    @abstractmethod
    def create_from_ai_data(cls, ai_summary: str, raw_data: Dict[str, Any], base_model: ModelBaseModel):
        pass

    class Meta:
        abstract = True
