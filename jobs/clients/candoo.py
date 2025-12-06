from typing import List

from django.conf import settings

from common.client import RestClient
from companies.models import Company, Perk
from jobs.models import Opportunity
from common.enums import ContractType, Currency
from locations.enums import LocationType, LocationLevel
from locations.models import Location
from jobs.enums import MilitaryService, ExperienceLevel, Gender
from common.cache import cache_for


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
    def __init__(self, client_name: str):
        super().__init__("https://careerapi.hrcando.ir")
        self.address = settings.CANDOO_HR_CLIENTS[client_name]["address"]
        self.auth_key = settings.CANDOO_HR_CLIENTS[client_name]["auth_key"]
        self.client_name = client_name

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

    @cache_for(24 * 60 * 60, ignore_self=True)
    def get_headers_and_footers(self) -> dict:
        return self.get_json_response("/api/v1/CareerPage/GetCareerPageHeaderFooterData").get("data")

    @cache_for(24 * 60 * 60, ignore_self=True)
    def get_about_us(self) -> dict:
        return self.get_json_response("/api/v1/CareerPage/GetAboutUsModuleData").get("data")

    @cache_for(24 * 60 * 60, ignore_self=True)
    def get_benefits(self) -> dict:
        return self.get_json_response("/api/v1/CareerPage/GetCompanyBenefitsModuleData").get("data")

    @cache_for(24 * 60 * 60, ignore_self=True)
    def get_jobs(self) -> dict:
        return self.get_json_response(
            "/api/v1/CareerPage/GetCareerPageJobList",
            "POST",
            data={"take": 10, "pageNumber": 1, "title": "", "departmentId": "", "cityId": "", "branchId": ""},
        ).get("data")

    @cache_for(24 * 60 * 60, ignore_self=True)
    def get_job_details(self, job_guid: str) -> dict:
        return self.get_json_response(
            f"/api/v1/CareerPage/GetCareerPageJobPageInfoByJobGuid/{job_guid}",
            "GET",
            url_params={"job_guid": job_guid},
        ).get("data")

    def get_company(self) -> Company:
        company, _ = Company.objects.update_or_create(
            name=self.get_company_name(),
            defaults={
                "description": self.get_company_description(),
                "page": self.get_company_page(),
                "image": self.get_company_image(),
                "size": self.get_company_size(),
                "location": self.get_company_location(),
            },
        )

        company.perks.all().delete()
        for benefit in self.get_benefits().get("companyBenefitModuleDetailsList", []):
            perk_name = BENEFITS.get(benefit.get("benefitId"))
            if perk_name:
                Perk.objects.get_or_create(name=perk_name, company=company)
        return company

    def get_company_name(self) -> str:
        return self.client_name

    def get_company_description(self) -> str:
        return self.get_about_us().get("aboutUsDescription")

    def get_company_page(self) -> str:
        return self.get_headers_and_footers().get("headerData", {}).get("webSiteAddress")

    def get_company_image(self) -> str:
        return self.get_headers_and_footers().get("headerData", {}).get("logoFileUrl")

    def get_company_perks(self) -> List[Perk]:
        try:
            company = Company.objects.get(name=self.get_company_name())
            return list(company.perks.all())
        except Company.DoesNotExist:
            return []

    def get_opportunities_id(self) -> List[str]:
        return [job.get("jobGuid") for job in self.get_jobs().get("jobs")]

    def _map_contract_type(self, work_type: dict) -> ContractType:
        if not work_type:
            return ContractType.OTHER

        work_type_name = work_type.get("name", "").strip()
        if "تمام وقت" in work_type_name or "تمام‌وقت" in work_type_name:
            return ContractType.FULL_TIME
        elif "پاره وقت" in work_type_name or "پاره‌وقت" in work_type_name:
            return ContractType.PART_TIME
        else:
            return ContractType.OTHER

    def _map_experience_level(self, seniority_level: dict) -> ExperienceLevel:
        if not seniority_level:
            return ExperienceLevel.OTHER

        level_name = seniority_level.get("name", "").strip()
        if any(term in level_name for term in ["کارآموز", "جونیور", "تازه کار"]):
            return ExperienceLevel.ENTRY
        elif any(term in level_name for term in ["کارشناس", "میان‌رده", "میان رده"]):
            return ExperienceLevel.MID
        elif any(term in level_name for term in ["ارشد", "سنیور", "کارشناس ارشد"]):
            return ExperienceLevel.SENIOR
        elif any(term in level_name for term in ["اصلی", "رئیس", "مدیر"]):
            return ExperienceLevel.PRINCIPAL
        else:
            return ExperienceLevel.OTHER

    def _map_gender(self, preferred_gender: dict) -> Gender:
        if not preferred_gender:
            return Gender.ANY

        gender_name = preferred_gender.get("name", "").strip()
        if "مرد" in gender_name or "آقا" in gender_name or "مذکر" in gender_name:
            return Gender.MALE
        elif "زن" in gender_name or "خانم" in gender_name or "مونث" in gender_name:
            return Gender.FEMALE
        else:
            return Gender.ANY

    def _map_location(self, location_name):
        if "تهران" in location_name or "Tehran" in location_name:
            location, _ = Location.objects.get_or_create(name="Tehran", level=LocationLevel.CITY)
            return location

        location, _ = Location.objects.get_or_create(name="Iran", level=LocationLevel.COUNTRY)
        return location

    def get_opportunity_by_id(self, opportunity_id: str) -> Opportunity:
        job_details = self.get_job_details(opportunity_id)

        opportunity, _ = Opportunity.objects.update_or_create(
            reference_id=opportunity_id,
            company=self.get_company(),
            defaults={
                "title": job_details.get("title"),
                "description": job_details.get("description"),
                "location_type": (
                    LocationType.ON_SITE if not job_details.get("isRemote", False) else LocationType.REMOTE
                ),
                "location": self._map_location(job_details.get("city", {}).get("name")),
                "contract_type": self._map_contract_type(job_details.get("workType")),
                "experience_level": self._map_experience_level(job_details.get("seniorityLevel")),
                "gender": self._map_gender(job_details.get("preferredGender")),
                "military_service": MilitaryService.ANY,
                "minimum_education_level": None,
                "minimum_experience_years": job_details.get("requiredExperienceYear"),
                "minimum_salary": job_details.get("minSalary"),
                "currency": Currency.IRR,
                "raw_details": job_details,
                "is_active": True,
            },
        )
        return opportunity
