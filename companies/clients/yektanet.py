from companies.clients.candoo import CandooClient
from companies.interfaces import CareerSiteClient
from companies.enums import CompanySize


class YektanetClient(CandooClient, CareerSiteClient):
    def __init__(self):
        super().__init__("Yektanet")
        
    def get_company_name(self) -> str:
        return "Yektanet"

    def get_company_size(self) -> CompanySize:
        return CompanySize.LARGE

    def get_company_location(self) -> str:
        return "Tehran"
