from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from companies.enums import CompanySize


@dataclass
class CompanyInfoDto:
    company_name: str
    size: CompanySize
    location_name: str
    perks: List[str]
    extra_info: Dict[str, Any]


@dataclass
class OpportunityDetailDto:
    job_title: Optional[str]
    location_name: str
    extra_info: Dict[str, Any]
