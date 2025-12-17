import logging

from celery import shared_task

from companies.clients import YektanetClient
from jobs.services import OpportunityService


logger = logging.getLogger(__name__)
clients = [YektanetClient()]


@shared_task
def update_opportunities():
    for client in clients:
        opportunity_service = OpportunityService(client)
        try:
            opportunities_id = client.get_opportunities_id()
            for opportunity_id in opportunities_id:
                try:
                    opportunity_service.get_or_create_opportunity(opportunity_id)
                    logger.info(f"Processed opportunity {opportunity_id}")
                except Exception as e:
                    logger.error(f"Failed to process opportunity {opportunity_id}: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch opportunities from {client}: {e}")
