from companies.interfaces import CareerSiteClient
from common.services import AIGeneratableService, EmbeddingService
from companies.models import Company, Perk
from locations.models import Location


class CompanyService:
    def __init__(self, careers_site_client: CareerSiteClient):
        self.careers_site_client = careers_site_client

    def get_or_create_company(self) -> Company:
        company_gen_srv = AIGeneratableService(Company)
        location_embedding_srv = EmbeddingService(Location)
        perk_embedding_srv = EmbeddingService(Perk)

        company_info = self.careers_site_client.get_company_info()
        perks = [perk_embedding_srv.get_or_create_item(perk) for perk in company_info.perks if perk]

        if company_info.location_name:
            company_location = location_embedding_srv.get_or_create_item(company_info.location_name)
        else:
            company_location = None

        return company_gen_srv.generate_model_from_raw_data(
            company_info.extra_info,
            default_values={
                "company_name": company_info.company_name,
                "location": company_location,
                "size": company_info.size,
                "perks": perks,
            },
        )
