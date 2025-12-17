from typing import List

from common import cache
from common.services import EmbeddingService, CacheService
from locations.models import Location


class LocationService:
    def __init__(self):
        self.location_embedding_srv = EmbeddingService(Location)
        self.cache_service = CacheService(prefix="location-service")

    def get_or_create_locations(self, location_names: List[str]) -> List[Location]:
        return self.location_embedding_srv.get_or_create_items(
            location_names,
            self.cache_service,
            tags=[["location-service", location_name] for location_name in location_names],
        )
