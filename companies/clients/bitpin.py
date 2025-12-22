from companies.clients.candoo import CandooClient
from companies.interfaces import CareerSiteClient
from companies.enums import CompanySize


class BitpinClient(CandooClient, CareerSiteClient):
    def __init__(self, page_size: int = 100):
        super().__init__("Bitpin", page_size)
        
    def get_company_name(self) -> str:
        return "Bitpin"

    def get_company_size(self) -> CompanySize:
        return CompanySize.LARGE

    def get_company_location(self) -> str:
        return "Tehran"
