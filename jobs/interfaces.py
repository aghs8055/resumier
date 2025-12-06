from typing import List
from abc import ABC, abstractmethod

from jobs.models import Opportunity
from companies.models import Company, Perk
from companies.enums import CompanySize
from locations.models import Location


class CareerSiteClient(ABC):
    @abstractmethod
    def get_company(self) -> Company:
        pass

    @abstractmethod
    def get_company_name(self) -> str:
        pass

    @abstractmethod
    def get_company_description(self) -> str:
        pass

    @abstractmethod
    def get_company_page(self) -> str:
        pass

    @abstractmethod
    def get_company_image(self) -> str:
        pass

    @abstractmethod
    def get_company_size(self) -> CompanySize:
        pass

    @abstractmethod
    def get_company_location(self) -> Location:
        pass

    @abstractmethod
    def get_company_perks(self) -> List[Perk]:
        pass
    
    @abstractmethod
    def get_opportunities_id(self) -> List[str]:
        pass

    @abstractmethod
    def get_opportunity_by_id(self, opportunity_id: str) -> Opportunity:
        pass
