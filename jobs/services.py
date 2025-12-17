import json
from typing import List

from companies.interfaces import CareerSiteClient
from jobs.models import Opportunity, JobCategory
from common.services import AIGeneratableService, EmbeddingService, CacheService
from companies.services import CompanyService
from locations.services import LocationService


class JobCategoryService:
    def __init__(self):
        self.job_category_embedding_srv = EmbeddingService(JobCategory)
        self.cache_service = CacheService(prefix="job-category-service")
        
    def get_or_create_job_categories(self, job_category_names: List[str]) -> List[JobCategory]:
        return self.job_category_embedding_srv.get_or_create_items(
            job_category_names,
            self.cache_service,
            tags=[["job-category-service", job_category_name] for job_category_name in job_category_names],
        )


class OpportunityService:
    def __init__(
        self,
        careers_site_client: CareerSiteClient,
        location_service: LocationService,
        company_service: CompanyService,
        job_category_service: JobCategoryService,
    ):
        self.opportunity_gen_srv = AIGeneratableService(Opportunity)
        self.careers_site_client = careers_site_client
        self.location_service = location_service
        self.company_service = company_service
        self.job_category_service = job_category_service
        self.cache_service = CacheService(prefix="opportunity-service")

    def get_or_create_opportunities(self, job_ids: List[str]) -> List[Opportunity]:
        company = self.company_service.get_or_create_company()
        opportunities_detail = []
        for job_id in job_ids:
            opportunities_detail.append(self.careers_site_client.get_opportunity_detail(job_id))

        location_names = [opportunity_detail.location_name for opportunity_detail in opportunities_detail]
        locations = self.location_service.get_or_create_locations(location_names)

        job_category_names = [opportunity_detail.job_title for opportunity_detail in opportunities_detail]
        job_categories = self.job_category_service.get_or_create_job_categories(job_category_names)

        return self.opportunity_gen_srv.generate_models_from_raw_data(
            [opportunity_detail.extra_info for opportunity_detail in opportunities_detail],
            self.cache_service,
            default_values=[
                {"company": company, "location": location, "reference_id": job_id, "category": category}
                for job_id, location, category in zip(job_ids, locations, job_categories)
            ],
            tags=[["job-service", company.name, job_id] for job_id in job_ids],
            cache_keys=[f"{company.name}:{job_id}" for job_id in job_ids],
        )
