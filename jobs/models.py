from django.db import models

from companies.models import Company
from jobs.enums import ExperienceLevel, Gender, JobCategory, MilitaryService
from common.enums import ContractType, EducationLevel, Currency
from locations.enums import LocationType
from locations.models import Location


class Opportunity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='opportunities')
    location_type = models.CharField(max_length=255, choices=LocationType.choices())
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='opportunities')
    contract_type = models.CharField(max_length=255, choices=ContractType.choices())
    experience_level = models.CharField(max_length=255, choices=ExperienceLevel.choices())
    gender = models.CharField(max_length=255, choices=Gender.choices())
    category = models.CharField(max_length=255, choices=JobCategory.choices())
    military_service = models.CharField(max_length=255, choices=MilitaryService.choices())
    minimum_education_level = models.CharField(max_length=255, choices=EducationLevel.choices())
    minimum_experience_years = models.IntegerField(null=True, blank=True)
    minimum_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=255, choices=Currency.choices())
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
