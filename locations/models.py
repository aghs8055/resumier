from typing import Literal, Type, Optional, Dict, Any
from django.db import models
from pydantic import Field, BaseModel

from locations.enums import LocationLevel
from common.models import TimedModel, EmbeddedModelLargeMixin


class Location(TimedModel, EmbeddedModelLargeMixin):
    SCHEMA_FIELDS = ['name', 'level']
    class ModelBaseModel(BaseModel):
        name: str = Field(..., description="The name of the location in Title Case format")
        level: Literal[LocationLevel.GLOBAL.value, LocationLevel.CONTINENT.value, LocationLevel.COUNTRY.value, LocationLevel.CITY.value]


    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=LocationLevel.choices())
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    
    @classmethod
    def create_from_base_model(cls, base_model: ModelBaseModel, _: Optional[Dict[str, Any]] = None):
        location, created = cls.objects.get_or_create(name=base_model.name, level=base_model.level)
        if created:
            location.save(update_embedding=True)
        return location
    
    def get_embedding_key(self) -> str:
        if self.parent is not None:
            return f"{self.parent.get_embedding_key()}/{self.level}:{self.name}"
        return f"{self.level}:{self.name}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        unique_together = ('name', 'level')
        ordering = ['-created_at']