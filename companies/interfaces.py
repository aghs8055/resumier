from typing import List, Dict, Any
from abc import ABC, abstractmethod


class CareerSiteClient(ABC):
    @abstractmethod
    def get_company_info(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_opportunities_id(self) -> List[str]:
        pass

    @abstractmethod
    def get_opportunity_detail(self, opportunity_id: str) -> Dict[str, Any]:
        pass
