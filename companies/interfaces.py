from typing import List, Dict, Any
from abc import ABC, abstractmethod

from companies.dto import CompanyInfoDto, OpportunityDetailDto


class CareerSiteClient(ABC):
    @abstractmethod
    def get_company_info(self) -> CompanyInfoDto:
        pass

    @abstractmethod
    def get_opportunities_id(self) -> List[str]:
        pass

    @abstractmethod
    def get_opportunity_detail(self, opportunity_id: str) -> OpportunityDetailDto:
        pass
