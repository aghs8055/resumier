from typing import Type, List, TypeVar, Generic, Dict, Any

from pgvector.django import CosineDistance
from langfuse.openai import OpenAI
from django.conf import settings
from pydantic import BaseModel, Field

from common.prompts import EMBEDDING_SERVICE_SYSTEM_PROMPT_V1, EMBEDDING_SERVICE_USER_PROMPT_V1
from common.models import EmbeddedModelSmall, EmbeddedModelLarge


T = TypeVar('T', bound=EmbeddedModelSmall | EmbeddedModelLarge)


class ObjectSelection(BaseModel):
    object_id: int = Field(..., description='The ID of the object to select')
    

class ObjectCreation(BaseModel):
    properties: Dict[str, Any] = Field(..., description='The properties of the object to create')
    
    
class Result(BaseModel):
    result: ObjectSelection | ObjectCreation


class EmbeddingService(Generic[T]): 
    def __init__(self, model: Type[T], llm_model: str = 'gpt-5-mini', embedding_model: str = 'text-embedding-3-large'):
        self.model = model
        self.client = OpenAI(**settings.LLM_SETTINGS['default'])
    
    def get_similar_items(self, embedding: List[float], k: int = 10, threshold: float = 0.0) -> List[T]:
        return list(
            self.model.objects
            .annotate(distance=CosineDistance('embedding', embedding))
            .order_by('distance')
            .filter(distance__lte=threshold)
            [:k]
        )
        
    def get_or_create_item(self, key: str, k: int = 10, threshold: float = 0.0) -> T:
        embedding = self.client.embeddings.create(input=key, model=self.embedding_model)
        similar_items = self.get_similar_items(embedding.data[0].embedding, k, threshold)
        
        resp = self.client.responses.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": EMBEDDING_SERVICE_SYSTEM_PROMPT_V1.format(model_schema=self.model.get_schema())},
                {"role": "user", "content": EMBEDDING_SERVICE_USER_PROMPT_V1.format(key=key, similar_items=similar_items)}
            ],
            Output=Result,
        ).parsed
        
        if isinstance(resp.result, ObjectSelection):
            return self.model.objects.get(id=resp.result.object_id)
        else:
            return ObjectCreation(**resp.result.properties)
