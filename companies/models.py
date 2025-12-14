from django.db import models
from pydantic import BaseModel, Field

from companies.enums import CompanySize
from companies.storages import CompanyLogoStorage
from locations.models import Location
from common.models import TimedModel, EmbeddedModelLargeMixin


class Perk(TimedModel, EmbeddedModelLargeMixin):
    SCHEMA_FIELDS = ['name']
    class ModelBaseModel(BaseModel):
        name: str = Field(..., description="The name of the perk in Title Case format")
        description: str = Field(..., description="The description of the perk")
    
    name = models.CharField(max_length=255)
    description = models.TextField()

    def get_embedding_key(self) -> str:
        return f"{self.name}: {self.description}"
    
    @classmethod
    def create_from_schema(cls, base_model):
        return cls.objects.create(name=base_model.name, description=base_model.description)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Perk'
        verbose_name_plural = 'Perks'


class Company(TimedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    page = models.URLField(max_length=255)
    image = models.ImageField(upload_to='', storage=CompanyLogoStorage(), null=True, blank=True)
    size = models.CharField(max_length=255, choices=CompanySize.choices())
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, related_name='companies', null=True, blank=True)
    perks = models.ManyToManyField(Perk, related_name='companies')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']