from typing import Dict, Any, Optional, Literal

from django.db import models
from pydantic import BaseModel, Field

from companies.models import Company
from jobs.enums import Gender, MilitaryService
from common.enums import ContractType, EducationLevel, Currency, Language, ExperienceLevel
from locations.enums import LocationType
from locations.models import Location
from common.models import AIGeneratableMixin, TimedModel, EmbeddedModelLargeMixin


class JobCategory(TimedModel, EmbeddedModelLargeMixin):
    SCHEMA_FIELDS = ["name", "description"]

    class ModelBaseModel(BaseModel):
        name: str = Field(..., description="Name of general category that the job title belongs to in Title Case format. Note that this is not the job title, it's the category of the job title.")
        description: str = Field(..., description="The description of the category and the jobs that can be placed in this category")

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def get_embedding_key(self) -> str:
        return self.name

    @classmethod
    def create_from_base_model(cls, base_model: ModelBaseModel, _: Optional[Dict[str, Any]] = None):
        category, created = cls.objects.update_or_create(
            name=base_model.name,
            defaults={
                "description": base_model.description,
            },
        )
        category.save(update_embedding=True)
        return category

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Job Category"
        verbose_name_plural = "Job Categories"


class Opportunity(EmbeddedModelLargeMixin, AIGeneratableMixin, TimedModel):
    SCHEMA_FIELDS = [
        "title",
        "description",
        "location_type",
        "location",
        "contract_type",
        "experience_level",
        "gender",
        "military_service",
        "minimum_education_level",
        "minimum_experience_years",
        "minimum_salary",
        "maximum_salary",
        "category",
        "currency",
        "language",
    ]

    class ModelBaseModel(BaseModel):
        job_page: str = Field(..., description="The page of the opportunity")
        title: str = Field(..., description="The title of the opportunity")
        description: str = Field(..., description="The description of the opportunity")
        location_type: Literal[LocationType.ON_SITE.value, LocationType.REMOTE.value, LocationType.HYBRID.value] = (
            Field(..., description="The type of location of the opportunity")
        )
        contract_type: Literal[
            ContractType.FULL_TIME.value,
            ContractType.PART_TIME.value,
            ContractType.CONTRACT.value,
            ContractType.VOLUNTEER.value,
            ContractType.OTHER.value,
        ] = Field(..., description="The contract type of the opportunity")
        experience_level: str = Field(..., description="The experience level of the opportunity")
        gender: Literal[Gender.MALE.value, Gender.FEMALE.value, Gender.ANY.value] = Field(
            ..., description="The gender of the opportunity"
        )
        military_service: Literal[
            MilitaryService.SHOULD_HAVE.value, MilitaryService.SHOULD_NOT_HAVE.value, MilitaryService.ANY.value
        ] = Field(..., description="The military service of the opportunity")
        minimum_education_level: Literal[
            EducationLevel.HIGH_SCHOOL.value,
            EducationLevel.BACHELOR.value,
            EducationLevel.MASTER.value,
            EducationLevel.DOCTORATE.value,
            EducationLevel.OTHER.value,
        ] = Field(..., description="The minimum education level of the opportunity")
        minimum_experience_years: int = Field(..., description="The minimum experience years of the opportunity")
        minimum_salary: float = Field(..., description="The minimum salary of the opportunity")
        maximum_salary: float = Field(..., description="The maximum salary of the opportunity")
        currency: Literal[Currency.USD.value, Currency.EUR.value, Currency.IRR.value, Currency.OTHER.value] = Field(
            ..., description="The currency of the opportunity"
        )
        language: Optional[Literal[Language.PERSIAN.value, Language.ENGLISH.value]] = Field(
            ..., description="The language of the opportunity"
        )

    reference_id = models.CharField(max_length=255, unique=True)
    job_page = models.URLField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="opportunities")
    location_type = models.CharField(max_length=255, choices=LocationType.choices(), null=True, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="opportunities", null=True, blank=True
    )
    contract_type = models.CharField(max_length=255, choices=ContractType.choices(), null=True, blank=True)
    experience_level = models.CharField(max_length=255, choices=ExperienceLevel.choices(), null=True, blank=True)
    gender = models.CharField(max_length=255, choices=Gender.choices(), null=True, blank=True)
    military_service = models.CharField(max_length=255, choices=MilitaryService.choices(), null=True, blank=True)
    minimum_education_level = models.CharField(max_length=255, choices=EducationLevel.choices(), null=True, blank=True)
    minimum_experience_years = models.IntegerField(null=True, blank=True)
    minimum_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    maximum_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(
        JobCategory, on_delete=models.CASCADE, related_name="opportunities", null=True, blank=True
    )
    currency = models.CharField(max_length=255, choices=Currency.choices(), null=True, blank=True)
    language = models.CharField(max_length=255, choices=Language.choices(), null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)
    ai_summary = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def create_from_base_model(cls, base_model: ModelBaseModel, default_values: Optional[Dict[str, Any]] = None):
        if default_values is None:
            raise ValueError("Default values are required")

        raw_data = default_values.get("raw_data")
        ai_summary = default_values.get("ai_summary")
        reference_id = default_values.get("reference_id")
        company = default_values.get("company")
        location = default_values.get("location")
        category = default_values.get("category")

        if raw_data is None:
            raise ValueError("Raw data is required")
        if ai_summary is None:
            raise ValueError("AI summary is required")
        if reference_id is None:
            raise ValueError("Reference ID is required")
        if company is None:
            raise ValueError("Company is required")

        opportunity, created = cls.objects.update_or_create(
            reference_id=reference_id,
            defaults={
                "job_page": base_model.job_page,
                "title": base_model.title,
                "description": base_model.description,
                "company": company,
                "location_type": base_model.location_type,
                "location": location,
                "contract_type": base_model.contract_type,
                "experience_level": base_model.experience_level,
                "gender": base_model.gender,
                "military_service": base_model.military_service,
                "minimum_education_level": base_model.minimum_education_level,
                "minimum_experience_years": base_model.minimum_experience_years,
                "minimum_salary": base_model.minimum_salary,
                "maximum_salary": base_model.maximum_salary,
                "currency": base_model.currency,
                "language": base_model.language,
                "raw_data": raw_data,
                "ai_summary": ai_summary,
                "is_active": True,
                "category": category,
            },
        )
        opportunity.save(update_embedding=True)
        return opportunity

    def get_embedding_key(self) -> str:
        return f"{self.title}: {self.description}/Summary: {self.ai_summary}"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = "Opportunities"
