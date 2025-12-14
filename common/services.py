from typing import Type, List, TypeVar, Generic, Union

from pgvector.django import CosineDistance
from openai import OpenAI
from django.conf import settings
from pydantic import BaseModel, Field, ConfigDict

from common.prompts import (
    EMBEDDING_SERVICE_SYSTEM_PROMPT_V1,
    EMBEDDING_SERVICE_USER_PROMPT_V1,
    AI_GENERATABLE_SERVICE_SYSTEM_PROMPT_V1,
    AI_GENERATABLE_SERVICE_USER_PROMPT_V1,
)
from common.models import EmbeddedModelSmallMixin, EmbeddedModelLargeMixin, AIGeneratableMixin


EmbeddingModelType = TypeVar("T", bound=EmbeddedModelSmallMixin | EmbeddedModelLargeMixin)


class EmbeddingService(Generic[EmbeddingModelType]):
    def __init__(
        self,
        model: Type[EmbeddingModelType],
        llm_model: str = "gpt-5-mini",
        embedding_model: str = "text-embedding-3-large",
    ):
        self.model = model
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.client = OpenAI(**settings.LLM_SETTINGS["default"])

    def get_similar_items(
        self, embedding: List[float], k: int = 10, threshold: float = 1.0
    ) -> List[EmbeddingModelType]:
        return [
            vars(obj)
            for obj in self.model.objects.annotate(distance=CosineDistance("embedding", embedding))
            .order_by("distance")
            .filter(distance__lte=threshold)[:k]
        ]

    def get_or_create_item(self, key: str, k: int = 10, threshold: float = 1.0) -> EmbeddingModelType:
        class ObjectSelection(BaseModel):
            model_config = ConfigDict(extra="forbid")
            object_id: int = Field(..., description="The ID of the object to select")

        class Result(BaseModel):
            model_config = ConfigDict(extra="forbid")
            result: Union[ObjectSelection, self.model.ModelBaseModel]

        embedding = self.client.embeddings.create(input=key, model=self.embedding_model)
        similar_items = self.get_similar_items(embedding.data[0].embedding, k, threshold)

        resp = self.client.responses.parse(
            model=self.llm_model,
            input=[
                {
                    "role": "system",
                    "content": EMBEDDING_SERVICE_SYSTEM_PROMPT_V1.format(model_schema=self.model.get_schema()),
                },
                {
                    "role": "user",
                    "content": EMBEDDING_SERVICE_USER_PROMPT_V1.format(key=key, similar_items=similar_items),
                },
            ],
            text_format=Result,
        ).output_parsed

        if isinstance(resp.result, ObjectSelection):
            return self.model.objects.get(id=resp.result.object_id)
        else:
            return self.model.create_from_schema(resp.result)


AIGeneratableModelType = TypeVar("AIGeneratableModelType", bound=AIGeneratableMixin)


class AIGeneratableService(Generic[AIGeneratableModelType]):
    def __init__(self, model: Type[AIGeneratableModelType], llm_model: str = "gpt-5-mini"):
        self.model = model
        self.llm_model = llm_model
        self.client = OpenAI(**settings.LLM_SETTINGS["default"])

    def generate_model_from_raw_data(self, raw_data: dict) -> AIGeneratableModelType:
        class Result(BaseModel):
            model_config = ConfigDict(extra="forbid")
            summary: str = Field(..., description="The summary of the model")
            model: self.model.ModelBaseModel = Field(..., description="The model")

        resp = self.client.responses.parse(
            model=self.llm_model,
            input=[
                {
                    "role": "system",
                    "content": AI_GENERATABLE_SERVICE_SYSTEM_PROMPT_V1.format(model_schema=self.model.get_schema()),
                },
                {
                    "role": "user",
                    "content": AI_GENERATABLE_SERVICE_USER_PROMPT_V1.format(raw_data=raw_data),
                },
            ],
            text_format=Result,
        )
        return self.model.create_from_ai_data(resp.summary, raw_data, resp.output_parsed)
