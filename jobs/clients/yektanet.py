from jobs.clients.candoo import CandooClient
from jobs.interfaces import CareerSiteClient
from companies.enums import CompanySize
from locations.models import Location
from locations.enums import LocationLevel


class YektanetClient(CandooClient, CareerSiteClient):
    def __init__(self):
        super().__init__("Yektanet")

    def get_company_size(self) -> CompanySize:
        return CompanySize.LARGE

    def get_company_location(self) -> Location:
        location, _ = Location.objects.get_or_create(name="Tehran", level=LocationLevel.CITY)
        return location
