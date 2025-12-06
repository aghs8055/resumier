from django.db import models

from companies.enums import CompanySize
from locations.models import Location


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    page = models.URLField(max_length=255)
    image = models.ImageField(upload_to='companies/', null=True, blank=True)
    size = models.CharField(max_length=255, choices=CompanySize.choices())
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, related_name='companies', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']


class Perk(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='perks')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Perk'
        verbose_name_plural = 'Perks'