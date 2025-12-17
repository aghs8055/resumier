from datetime import timedelta
from typing import List

from django.utils import timezone

from companies.interfaces import CareerSiteClient
from common.services import AIGeneratableService, EmbeddingService, CacheService
from companies.models import Company, Perk
from locations.services import LocationService


class PerkService:
    def __init__(self):
        self.perk_embedding_srv = EmbeddingService(Perk)
        self.cache_service = CacheService(prefix="perk-service")

    def get_or_create_perks(self, perk_names: List[str]) -> List[Perk]:
        return self.perk_embedding_srv.get_or_create_items(
            perk_names, self.cache_service, tags=[["perk-service", perk] for perk in perk_names]
        )


class CompanyService:
    def __init__(
        self,
        careers_site_client: CareerSiteClient,
        location_service: LocationService,
        perk_service: PerkService,
        cache_ttl: int = 30 * 24 * 60 * 60,
    ):
        self.company_gen_srv = AIGeneratableService(Company)
        self.careers_site_client = careers_site_client
        self.location_service = location_service
        self.perk_service = perk_service
        self.cache_ttl = cache_ttl
        self.cache_service = CacheService(prefix="company-service")

    def get_or_create_company(self) -> Company:
        company_info = self.careers_site_client.get_company_info()
        perks = self.perk_service.get_or_create_perks([perk for perk in company_info.perks if perk])
        location = self.location_service.get_or_create_locations([company_info.location_name])[0]

        return self.company_gen_srv.generate_models_from_raw_data(
            [company_info.extra_info],
            self.cache_service,
            default_values=[
                {
                    "company_name": company_info.company_name,
                    "location": location,
                    "size": company_info.size,
                    "perks": perks,
                }
            ],
            tags=[["company-service", company_info.company_name]],
            cache_keys=[company_info.company_name],
        )[0]
