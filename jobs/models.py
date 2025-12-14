from django.db import models
from pydantic import BaseModel, Field

from companies.models import Company
from jobs.enums import Gender, MilitaryService
from common.enums import ContractType, EducationLevel, Currency, Language, ExperienceLevel
from locations.enums import LocationType
from locations.models import Location
from common.models import TimedModel, EmbeddedModelLargeMixin


class JobCategory(TimedModel, EmbeddedModelLargeMixin):
    SCHEMA_FIELDS = ['name', 'description']
    class ModelBaseModel(BaseModel):
        name: str = Field(..., description="The name of the job category in Title Case format")
        description: str = Field(..., description="The description of the job category")
        
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def get_embedding_key(self) -> str:
        return f"{self.name}: {self.description}"
    
    @classmethod
    def create_from_base_model(cls, base_model: ModelBaseModel):
        return cls.objects.create(name=base_model.name, description=base_model.description)
        

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'

class Opportunity(TimedModel):
    reference_id = models.CharField(max_length=255)
    job_page = models.URLField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='opportunities')
    location_type = models.CharField(max_length=255, choices=LocationType.choices(), null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='opportunities', null=True, blank=True)
    contract_type = models.CharField(max_length=255, choices=ContractType.choices(), null=True, blank=True)
    experience_level = models.CharField(max_length=255, choices=ExperienceLevel.choices(), null=True, blank=True)
    gender = models.CharField(max_length=255, choices=Gender.choices(), null=True, blank=True)
    military_service = models.CharField(max_length=255, choices=MilitaryService.choices(), null=True, blank=True)
    minimum_education_level = models.CharField(max_length=255, choices=EducationLevel.choices(), null=True, blank=True)
    minimum_experience_years = models.IntegerField(null=True, blank=True)
    minimum_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    maximum_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='opportunities', null=True, blank=True)
    currency = models.CharField(max_length=255, choices=Currency.choices(), null=True, blank=True)
    language = models.CharField(max_length=255, choices=Language.choices(), null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)
    ai_summary = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
