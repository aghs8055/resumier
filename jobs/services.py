from companies.interfaces import CareerSiteClient
from jobs.models import Opportunity
from common.services import AIGeneratableService, EmbeddingService
from locations.models import Location
from companies.services import CompanyService

class OpportunityService:
    def __init__(self, careers_site_client: CareerSiteClient):
        self.careers_site_client = careers_site_client
        self.opportunity_gen_srv = AIGeneratableService(Opportunity)
        self.location_embedding_srv = EmbeddingService(Location)
        self.company_service = CompanyService(careers_site_client)
        
    def get_or_create_opportunity(self, job_id: str) -> Opportunity:
        company = self.company_service.get_or_create_company()
        opportunity_detail = self.careers_site_client.get_opportunity_detail(job_id)
        
        if opportunity_detail.location_name:
            location = self.location_embedding_srv.get_or_create_item(opportunity_detail.location_name)
        else:
            location = None

        return self.opportunity_gen_srv.generate_model_from_raw_data(
            opportunity_detail.extra_info,
            default_values={"company": company, "location": location, "reference_id": job_id},
        )
