from typing import List, Dict, Any

from django.conf import settings

from common.client import RestClient
from common.cache import cache_for
from companies.enums import CompanySize
from companies.dto import CompanyInfoDto, OpportunityDetailDto


BENEFITS = {
    13: "Remote work",
    14: "Training courses",
    16: "Military service exemption (Amriye)",
    17: "Commute shuttle service",
    18: "Insurance",
    19: "Supplemental insurance",
    20: "Game room",
    21: "Team building budget",
    23: "Occasional gifts",
    24: "Flexible working hours",
    25: "Breakfast and snacks",
    26: "Food and lunch",
    27: "Rest room",
    28: "Loans and installment purchases",
    29: "Psychologist and counseling",
    30: "Vending machine",
    31: "Organizational gatherings",
    32: "Medical facilities",
    33: "Organizational doctor",
    34: "Individual coaching for managers",
    35: "Training facilities",
    36: "Organizational discounts",
    37: "Cafe",
    38: "Food allowance",
}


class CandooClient(RestClient):
    def __init__(self, client_name: str, page_size: int = 100):
        super().__init__("https://careerapi.hrcando.ir")
        self.address = settings.CANDOO_HR_CLIENTS[client_name]["address"]
        self.auth_key = settings.CANDOO_HR_CLIENTS[client_name]["auth_key"]
        self.client_name = client_name
        self.page_size = page_size

    def get_json_response(
        self,
        url: str,
        method: str = "GET",
        url_params: dict = None,
        data: dict = None,
        headers: dict = None,
        params: dict = None,
        timeout: int = 10,
    ) -> dict:
        headers = {
            "address": self.address,
            "careerauthkey": self.auth_key,
        }
        return super().get_json_response(url, method, url_params, data, headers, params, timeout)

    def get_headers_and_footers(self) -> dict:
        @cache_for(24 * 60 * 60, key_prefix=f"candoo:{self.client_name}")
        def _get_headers_and_footers():
            return self.get_json_response("/api/v1/CareerPage/GetCareerPageHeaderFooterData").get("data")
        return _get_headers_and_footers()

    def get_about_us(self) -> dict:
        @cache_for(24 * 60 * 60, key_prefix=f"candoo:{self.client_name}")
        def _get_about_us():
            return self.get_json_response("/api/v1/CareerPage/GetAboutUsModuleData").get("data")
        return _get_about_us()

    def get_benefits(self) -> List[str]:
        @cache_for(24 * 60 * 60, key_prefix=f"candoo:{self.client_name}")
        def _get_benefits():
            benefits = self.get_json_response("/api/v1/CareerPage/GetCompanyBenefitsModuleData").get("data")
            return [BENEFITS.get(benefit.get("benefitId")) for benefit in benefits.get("companyBenefitModuleDetailsList", [])]
        return _get_benefits()

    def get_jobs(self) -> dict:
        @cache_for(24 * 60 * 60, key_prefix=f"candoo:{self.client_name}")
        def _get_jobs():
            return self.get_json_response(
                "/api/v1/CareerPage/GetCareerPageJobList",
                "POST",
                data={"take": self.page_size, "pageNumber": 1, "title": "", "departmentId": "", "cityId": "", "branchId": ""},
            ).get("data")
        return _get_jobs()

    def get_job_details(self, job_guid: str) -> dict:
        @cache_for(24 * 60 * 60, key_prefix=f"candoo:{self.client_name}")
        def _get_job_details(job_guid):
            return self.get_json_response(
                f"/api/v1/CareerPage/GetCareerPageJobPageInfoByJobGuid/{job_guid}",
                "GET",
                url_params={"job_guid": job_guid},
            ).get("data")
        return _get_job_details(job_guid)

    def get_company_size(self) -> CompanySize:
        raise NotImplementedError("get_company_size is not implemented")

    def get_company_location(self) -> str:
        raise NotImplementedError("get_company_location is not implemented")

    def get_company_info(self) -> CompanyInfoDto:
        return CompanyInfoDto(
            company_name=self.get_company_name(),
            size=self.get_company_size(),
            location_name=self.get_company_location(),
            perks=self.get_benefits(),
            extra_info={
                "header_and_footer": self.get_headers_and_footers(),
                "about_us": self.get_about_us(),
            },
        )

    def get_opportunities_id(self) -> List[str]:
        return [job.get("jobGuid") for job in self.get_jobs().get("jobs")]


    def get_opportunity_detail(self, opportunity_id: str) -> OpportunityDetailDto:
        job_details = self.get_job_details(opportunity_id)
        return OpportunityDetailDto(
            job_title=job_details.get("title"),
            location_name=job_details.get("city", {}).get("name", "global"),
            extra_info={
                **job_details,
                "job_page": f"{self.address}/job-detail/{opportunity_id}",
            },
        )

