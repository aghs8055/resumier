import logging
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlparse
import os

from django.db import models
from django.core.files.base import ContentFile
from pydantic import BaseModel, Field

from companies.enums import CompanySize
from companies.storages import CompanyLogoStorage
from locations.models import Location
from common.models import TimedModel, EmbeddedModelLargeMixin, AIGeneratableMixin


logger = logging.getLogger(__name__)


class Perk(TimedModel, EmbeddedModelLargeMixin):
    SCHEMA_FIELDS = ["name"]

    class ModelBaseModel(BaseModel):
        name: str = Field(..., description="The name of the perk in Title Case format")
        description: str = Field(..., description="The description of the perk")

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def get_embedding_key(self) -> str:
        return f"{self.name}: {self.description}"

    @classmethod
    def create_from_base_model(cls, base_model: ModelBaseModel, _: Optional[Dict[str, Any]] = None):
        perk, created = cls.objects.update_or_create(
            name=base_model.name,
            defaults={
                "description": base_model.description,
            },
        )
        perk.save(update_embedding=True)
        return perk

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Perk"
        verbose_name_plural = "Perks"


class Company(EmbeddedModelLargeMixin, AIGeneratableMixin, TimedModel):
    SCHEMA_FIELDS = ["name", "description", "page", "image"]

    class ModelBaseModel(BaseModel):
        name: str = Field(..., description="The name of the company in Title Case format")
        description: str = Field(..., description="The description of the company")
        page: str = Field(..., description="The page of the company")
        image: str = Field(..., description="The image of the company")

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    page = models.URLField(max_length=255)
    image = models.ImageField(upload_to="", storage=CompanyLogoStorage(), null=True, blank=True)
    size = models.CharField(max_length=255, choices=CompanySize.choices())
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, related_name="companies", null=True, blank=True)
    perks = models.ManyToManyField(Perk, related_name="companies")

    def get_embedding_key(self) -> str:
        return f"{self.name}: {self.description}"

    @staticmethod
    def download_image_from_url(image_url: str, company_name: str) -> Optional[ContentFile]:
        """Download image from URL and return as ContentFile for S3 upload"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Get file extension from URL or content type
            parsed_url = urlparse(image_url)
            file_extension = os.path.splitext(parsed_url.path)[1]
            
            if not file_extension:
                content_type = response.headers.get('content-type', '')
                if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                    file_extension = '.jpg'
                elif 'image/png' in content_type:
                    file_extension = '.png'
                elif 'image/webp' in content_type:
                    file_extension = '.webp'
                elif 'image/gif' in content_type:
                    file_extension = '.gif'
                else:
                    file_extension = '.jpg'
            
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_company_name = safe_company_name.replace(' ', '_')
            filename = f"{safe_company_name}_logo{file_extension}"
            
            return ContentFile(response.content, name=filename)
        except Exception as e:
            logger.error(f"Error downloading image from {image_url}: {e}")
            return None

    @classmethod
    def create_from_base_model(cls, base_model: ModelBaseModel, default_values: Optional[Dict[str, Any]] = None):
        if default_values is None:
            raise ValueError("Default values are required")

        company_name = default_values.get("company_name")
        location = default_values.get("location")
        perks = default_values.get("perks")
        size = default_values.get("size")
        raw_data = default_values.get("raw_data")
        ai_summary = default_values.get("ai_summary")

        if company_name is None:
            raise ValueError("Company name is required")
        if size is None:
            raise ValueError("Size is required")
        if location is None:
            raise ValueError("Location is required")
        if perks is None:
            raise ValueError("Perks are required")
        if raw_data is None:
            raise ValueError("Raw data is required")
        if ai_summary is None:
            raise ValueError("AI summary is required")

        image_file = None
        if base_model.image is not None:
            image_file = cls.download_image_from_url(base_model.image, company_name)

        company, created = cls.objects.update_or_create(
            name=company_name,
            defaults={
                "description": base_model.description,
                "page": base_model.page,
                "size": size,
                "location": location,
                "raw_data": raw_data,
                "ai_summary": ai_summary,
                "image": image_file,
            }
        )
        company.perks.set(perks)
        company.save(update_embedding=True)
        return company

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["-created_at"]
