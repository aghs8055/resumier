from django.db import models

from companies.models import Company
from jobs.enums import ExperienceLevel, Gender, MilitaryService
from common.enums import ContractType, EducationLevel, Currency
from locations.enums import LocationType
from locations.models import Location


class JobCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'

class Opportunity(models.Model):
    reference_id = models.CharField(max_length=255)
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
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='opportunities', null=True, blank=True)
    currency = models.CharField(max_length=255, choices=Currency.choices(), null=True, blank=True)
    raw_details = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
