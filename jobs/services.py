from typing import Dict, Any, List

from jobs.models import Opportunity


class JobMaker:
    def __init__(self):
        pass

    def convert_to_opportunity(self, raw_details: List[Dict[str, Any]]) -> List[Opportunity]:
        pass
