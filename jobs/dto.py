from pydantic import BaseModel, Field
from typing import Literal, Optional
from locations.enums import LocationType
from locations.models import Location
from common.enums import ContractType, EducationLevel, Currency
from jobs.enums import ExperienceLevel, Gender, MilitaryService
from jobs.models import JobCategory

class JobCreatorDTO(BaseModel):
    title: str = Field(..., description="The title of the job")
    description: str = Field(..., description="The description of the job")
    location_type: Literal[LocationType.ON_SITE, LocationType.REMOTE, LocationType.HYBRID] = Field(..., description="The type of the location")
    location: str = Field(..., description="The location of the job")
    contract_type: ContractType = Field(..., description="The type of the contract")
    experience_level: Optional[ExperienceLevel] = Field(..., description="The level of the experience")
    gender: Gender = Field(..., description="The gender of the job")
    military_service: Optional[MilitaryService] = Field(..., description="The military service of the job")
    minimum_education_level: Optional[EducationLevel] = Field(..., description="The minimum education level of the job") 
    minimum_experience_years: Optional[int] = Field(..., description="The minimum experience years of the job")
    minimum_salary: Optional[float] = Field(..., description="The minimum salary of the job")
    currency: Currency = Field(..., description="The currency of the job")
    category: Literal[*JobCategory.objects.all().values_list('name', flat=True)] = Field(..., description="The category of the job")