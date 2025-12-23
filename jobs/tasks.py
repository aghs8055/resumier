import logging

from celery import shared_task

from companies.clients import YektanetClient, BitpinClient
from jobs.services import OpportunityService
from locations.services import LocationService
from companies.services import CompanyService, PerkService
from jobs.services import JobCategoryService


logger = logging.getLogger(__name__)
clients = [YektanetClient(), BitpinClient()]


@shared_task
def update_opportunities():
    location_service = LocationService()
    job_category_service = JobCategoryService()
    perk_service = PerkService()
    for client in clients:
        company_service = CompanyService(client, location_service, perk_service)
        opportunity_service = OpportunityService(client, location_service, company_service, job_category_service)
        try:
            try:
                opportunity_service.get_or_create_opportunities(client.get_opportunities_id())
                logger.info(f"Processed opportunities from {client}")
            except Exception as e:
                logger.error(f"Failed to process opportunities from {client}: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch opportunities from {client}: {e}")
