from random import shuffle
from typing import Type, List, TypeVar, Generic, Union, Optional, Dict, Any, Set, Tuple
import json
import logging
import hashlib
from abc import ABC, abstractmethod
import re
from concurrent.futures import ThreadPoolExecutor

from langfuse import get_client, propagate_attributes
from django.core.cache import caches
from pgvector.django import CosineDistance
from django.conf import settings
from django.forms.models import model_to_dict
from pydantic import BaseModel, Field, ConfigDict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.messages import SystemMessage, HumanMessage
from langfuse.langchain import CallbackHandler

from common.prompts import (
    EMBEDDING_SERVICE_SYSTEM_PROMPT_V1,
    EMBEDDING_SERVICE_USER_PROMPT_V1,
    AI_GENERATABLE_SERVICE_SYSTEM_PROMPT_V1,
    AI_GENERATABLE_SERVICE_USER_PROMPT_V1,
)
from common.models import EmbeddedModelSmallMixin, EmbeddedModelLargeMixin, AIGeneratableMixin


logger = logging.getLogger(__name__)


class EvaluatableAgent(ABC):
    agent_name: str
    input_names: List[str]

    @abstractmethod
    def _execute(
        self, *args, **kwargs
    ) -> Tuple[BaseModel, Optional[Dict[str, Any]]] | Tuple[List[BaseModel], Optional[List[Dict[str, Any]]]]:
        pass

    def _get_metadata(self, resp: Dict[str, Any]) -> Dict[str, Any]:
        return vars(resp["raw"])

    def _validate_inputs_sizes(
        self,
        output: BaseModel | List[BaseModel],
        metadata: Optional[Dict[str, Any]] | Optional[List[Dict[str, Any]]],
        *args,
        tags: Optional[List[List[str]]] = None,
        **kwargs,
    ):
        """
        Validate that the sizes of output, args, tags, and kwargs are compatible.

        For single output (BaseModel): No validation needed
        For list output (List[BaseModel]): All args and kwargs values must be lists of the same length
        """
        if not isinstance(output, list):
            return

        output_length = len(output)

        for i, arg in enumerate(args):
            if not isinstance(arg, list):
                raise ValueError(
                    f"When output is a list, all args must be lists. "
                    f"Arg at position {i} (input_name: {self.input_names[i] if i < len(self.input_names) else 'unknown'}) is not a list."
                )
            if len(arg) != output_length:
                raise ValueError(
                    f"Arg at position {i} (input_name: {self.input_names[i] if i < len(self.input_names) else 'unknown'}) "
                    f"has length {len(arg)}, but output has length {output_length}. All must be the same length."
                )

        for key, value in kwargs.items():
            if not isinstance(value, list):
                raise ValueError(
                    f"When output is a list, all kwargs values must be lists. " f"Kwarg '{key}' is not a list."
                )
            if len(value) != output_length:
                raise ValueError(
                    f"Kwarg '{key}' has length {len(value)}, but output has length {output_length}. "
                    f"All must be the same length."
                )

        if tags is not None:
            if not isinstance(tags, list):
                raise ValueError("When output is a list, tags must be a list of lists or None.")
            if len(tags) != output_length:
                raise ValueError(
                    f"Tags list has length {len(tags)}, but output has length {output_length}. "
                    f"All must be the same length."
                )

        if metadata is not None:
            if isinstance(metadata, list):
                if len(metadata) != output_length:
                    raise ValueError(
                        f"Metadata list has length {len(metadata)}, but output has length {output_length}. "
                        f"All must be the same length."
                    )
            else:
                if not isinstance(metadata, dict):
                    raise ValueError("Metadata must be a dict or a list of dicts.")

    def _log_trace(
        self,
        inputs: Dict[str, Any],
        output: BaseModel,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ):
        langfuse = get_client()

        with propagate_attributes(tags=tags or []):
            langfuse.start_observation(
                name=self.agent_name,
                input=inputs,
                output=output,
                model=self.llm_model,
                metadata=metadata,
            ).end()

    def execute(self, *args, tags: Optional[List[str] | List[List[str]]] = None, **kwargs) -> Any:
        output, metadata = self._execute(*args, **kwargs)

        try:
            self._validate_inputs_sizes(output, metadata, *args, tags=tags, **kwargs)
        except ValueError as e:
            logger.error(f"Error validating inputs sizes: {e}")
            return output

        if isinstance(output, BaseModel):
            inputs = kwargs.copy()
            inputs.update({name: value for name, value in zip(self.input_names, args)})
            self._log_trace(inputs, output, metadata, tags)
        else:
            for i, result in enumerate(output):
                inputs = {k: v[i] for k, v in kwargs.items()}
                inputs.update({name: value[i] for name, value in zip(self.input_names, args)})
                self._log_trace(inputs, result, metadata[i] if metadata else None, tags[i] if tags else None)

        langfuse = get_client()
        langfuse.flush()

        return output


class CacheService:
    def __init__(self, prefix: str, cache_name: str = "default", cache_ttl: int = 30 * 24 * 60 * 60):
        self.prefix = prefix
        self.cache_ttl = cache_ttl
        self.cache = caches[cache_name]

    @staticmethod
    def sanitize_key(key: str, max_length: int = 200) -> str:
        """
        Sanitize cache key to be memcached-compatible.

        - Removes/replaces whitespace and special characters
        - Hashes if the key is too long
        - Returns a safe ASCII string
        """
        sanitized = re.sub(r"[^\w\-.]", "_", key)

        sanitized = re.sub(r"_+", "_", sanitized)

        if len(sanitized) > max_length:
            prefix_len = max_length - 33
            sanitized = f"{sanitized[:prefix_len]}_{hashlib.md5(key.encode()).hexdigest()}"

        return sanitized

    def get_cached_keys(self, keys: List[str]) -> List[str]:
        return list({key for key in keys if self.cache.get(f"{self.prefix}:{self.sanitize_key(key)}") is not None})

    def get_uncached_keys(self, keys: List[str]) -> Set[str]:
        return {key for key in keys if key not in self.get_cached_keys(keys)}

    def set_cache_values(self, keys: List[str], values: List[Any]):
        for key, value in zip(keys, values):
            self.cache.set(f"{self.prefix}:{self.sanitize_key(key)}", value, self.cache_ttl)

    def get_cached_values(self, keys: List[str]) -> List[Any]:
        return [self.cache.get(f"{self.prefix}:{self.sanitize_key(key)}") for key in keys]


class BulkLLMCaller:
    def __init__(self, base_model: Type[BaseModel], llm_model: str = "gpt-5-mini"):
        self.client = ChatOpenAI(
            **settings.LLM_SETTINGS["default"], model=llm_model, reasoning={"effort": "medium", "summary": "auto"}
        ).with_structured_output(base_model, include_raw=True)
        self.data = []
        self.tags = []

    def add_task(self, inputs: List, tags: Optional[List[str]] = None):
        self.data.append(inputs)
        self.tags.append(tags)

    def _call(self, inputs: List, tags: Optional[List[str]] = None):
        langfuse_handler = CallbackHandler()
        return self.client.invoke(inputs, config={"callbacks": [langfuse_handler], "tags": tags})

    def call(self):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._call, inputs, tags) for inputs, tags in zip(self.data, self.tags)]
            resps = [future.result() for future in futures]
        self.data.clear()
        self.tags.clear()
        return resps


EmbeddingModelType = TypeVar("T", bound=EmbeddedModelSmallMixin | EmbeddedModelLargeMixin)


class ObjectSelection(BaseModel):
    """Represents a selection of an existing object by ID."""

    model_config = ConfigDict(extra="forbid")
    object_id: int = Field(..., description="The ID of the object to select")


class ModelFinderAgent(EvaluatableAgent):
    agent_name = "model_finder_agent"
    input_names = ["keys", "similar_items"]

    def __init__(self, model: Type[EmbeddingModelType], llm_model: str = "gpt-5-mini"):
        self.model = model
        self.llm_model = llm_model
        self.client = ChatOpenAI(**settings.LLM_SETTINGS["default"], model=llm_model, reasoning={"effort": "medium", "summary": "auto"})

    def _execute(
        self,
        keys: List[str],
        similar_items: List[List[str]],
        tags: Optional[List[List[str]]] = None,
    ) -> Tuple[List[EmbeddingModelType], Optional[List[Dict[str, Any]]]]:
        class Result(BaseModel):
            model_config = ConfigDict(extra="forbid")
            result: Union[ObjectSelection, self.model.ModelBaseModel]

        if tags is None:
            tags = [None] * len(keys)

        res = []
        metadata = []
        structured_client = self.client.with_structured_output(Result, include_raw=True)
        for key, tag, similars in zip(keys, tags, similar_items):
            langfuse_handler = CallbackHandler()
            resp = structured_client.invoke(
                [
                    SystemMessage(
                        content=EMBEDDING_SERVICE_SYSTEM_PROMPT_V1.format(
                            model_schema=json.dumps(self.model.get_schema(), indent=4)
                        )
                    ),
                    HumanMessage(
                        content=EMBEDDING_SERVICE_USER_PROMPT_V1.format(
                            key=key, similar_items="\n===========\n".join(similars)
                        )
                    ),
                ],
                config={"callbacks": [langfuse_handler], "tags": tag or ["embedding-service", self.model.__name__]},
            )
            res.append(resp["parsed"])
            metadata.append(self._get_metadata(resp))
        return res, metadata


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
        self.agent = ModelFinderAgent(model, llm_model)

    def _convert_model_instance_to_str(self, instance: EmbeddingModelType) -> str:
        data = model_to_dict(instance)
        data.pop("embedding")
        return json.dumps(data, indent=4)

    def get_similar_items(self, embedding: List[float], k: int = 10, threshold: float = 2.0) -> List[str]:
        res = [
            self._convert_model_instance_to_str(obj)
            for obj in self.model.objects.annotate(distance=CosineDistance("embedding", embedding))
            .order_by("distance")
            .filter(distance__lte=threshold)[:k]
        ]
        shuffle(res)
        return res

    def _get_or_create_items(
        self,
        keys: List[str],
        k: int = 10,
        threshold: float = 2.0,
        tags: Optional[List[List[str]]] = None,
    ) -> List[EmbeddingModelType]:
        embeddings_client = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=settings.LLM_SETTINGS["default"]["api_key"],
            openai_api_base=settings.LLM_SETTINGS["default"]["base_url"],
        )
        embeddings = embeddings_client.embed_documents(keys)
        similar_items = []
        for embedding in embeddings:
            similar_items.append(self.get_similar_items(embedding, k, threshold))
        resps = self.agent.execute(keys, similar_items, tags=tags)

        res = []
        for resp in resps:
            if isinstance(resp.result, ObjectSelection):
                model_obj = self.model.objects.get(id=resp.result.object_id)
            else:
                model_obj = self.model.create_from_base_model(resp.result)
            res.append(model_obj)
        return res

    def get_or_create_items(
        self,
        keys: List[str],
        cache_service: CacheService,
        k: int = 10,
        threshold: float = 2.0,
        tags: Optional[List[List[str]]] = None,
    ) -> List[EmbeddingModelType]:
        if tags is None:
            tags = [None] * len(keys)

        key_tags_map = {key: tag for key, tag in zip(keys, tags)}
        uncached_keys = list(cache_service.get_uncached_keys(keys))
        if uncached_keys:
            tags = [key_tags_map[key] for key in uncached_keys]
            new_items = self._get_or_create_items(uncached_keys, k, threshold, tags)
            cache_service.set_cache_values(uncached_keys, new_items)
        return cache_service.get_cached_values(keys)


AIGeneratableModelType = TypeVar("AIGeneratableModelType", bound=AIGeneratableMixin)


class ModelGenratorAgent(EvaluatableAgent):
    agent_name = "model_generator_agent"
    input_names = ["raw_data"]

    def __init__(self, model: Type[AIGeneratableModelType], llm_model: str = "gpt-5-mini"):
        self.model = model
        self.llm_model = llm_model

    def _execute(
        self,
        raw_data: List[Dict[str, Any]],
        tags: Optional[List[List[str]]] = None,
    ) -> Tuple[List[AIGeneratableModelType], Optional[Dict[str, Any]]]:
        class Result(BaseModel):
            model_config = ConfigDict(extra="forbid")
            summary: str = Field(
                ...,
                description="A comprehensive summary of the model in raw English text that keep all the details of the model. I will use it to find this model by embedding similarity search. It's about data, not the schema of data.",
            )
            model: self.model.ModelBaseModel = Field(..., description="The model")

        if tags is None:
            tags = [None] * len(raw_data)

        bulk_llm_caller = BulkLLMCaller(Result, self.llm_model)
        for data, tag in zip(raw_data, tags):
            bulk_llm_caller.add_task(
                [
                    SystemMessage(
                        content=AI_GENERATABLE_SERVICE_SYSTEM_PROMPT_V1.format(
                            model_schema=json.dumps(self.model.get_schema(), indent=4)
                        )
                    ),
                    HumanMessage(
                        content=AI_GENERATABLE_SERVICE_USER_PROMPT_V1.format(raw_data=json.dumps(data, indent=4))
                    ),
                ],
                tag or ["ai-generatable-service", self.model.__name__],
            )

        resps = bulk_llm_caller.call()

        res = []
        metadata = []
        for resp in resps:
            res.append(resp["parsed"])
            metadata.append(self._get_metadata(resp))
        return res, metadata


class AIGeneratableService(Generic[AIGeneratableModelType]):
    def __init__(self, model: Type[AIGeneratableModelType], llm_model: str = "gpt-5-mini"):
        self.model = model
        self.llm_model = llm_model
        self.agent = ModelGenratorAgent(model, llm_model)

    def _validate_inputs(
        self,
        raw_data: List[Dict[str, Any]],
        default_values: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[List[str]]] = None,
        cache_keys: Optional[List[str]] = None,
    ):
        if default_values is None:
            default_values = [None] * len(raw_data)

        if tags is None:
            tags = [None] * len(raw_data)

        if len(cache_keys) != len(raw_data):
            raise ValueError("Cache keys must be the same length as raw data")

        if len(default_values) != len(raw_data):
            raise ValueError("Default values must be the same length as raw data")

        if len(tags) != len(raw_data):
            raise ValueError("Tags must be the same length as raw data")

        return raw_data, default_values, tags, cache_keys

    def generate_models_from_raw_data(
        self,
        raw_data: List[Dict[str, Any]],
        cache_service: CacheService,
        cache_keys: List[str],
        default_values: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[List[str]]] = None,
    ) -> List[AIGeneratableModelType]:
        raw_data, default_values, tags, cache_keys = self._validate_inputs(raw_data, default_values, tags, cache_keys)
        key_tags_map = {key: tag for key, tag in zip(cache_keys, tags)}
        key_data_map = {key: data for key, data in zip(cache_keys, raw_data)}
        key_default_values_map = {key: dv for key, dv in zip(cache_keys, default_values)}
        uncached_keys = list(cache_service.get_uncached_keys(cache_keys))
        if uncached_keys:
            raw_data = [key_data_map[key] for key in uncached_keys]
            default_values = [key_default_values_map[key] for key in uncached_keys]
            tags = [key_tags_map[key] for key in uncached_keys]
            resps = self.agent.execute(raw_data, tags=tags)
            new_items = []
            for data, resp, defaults in zip(raw_data, resps, default_values):
                if defaults is None:
                    defaults = dict()
                defaults["ai_summary"] = resp.summary
                defaults["raw_data"] = data
                model_obj = self.model.create_from_base_model(resp.model, defaults)
                new_items.append(model_obj)
            cache_service.set_cache_values(uncached_keys, new_items)
        return cache_service.get_cached_values(cache_keys)
