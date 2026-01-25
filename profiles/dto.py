from typing import Optional, List, Literal
from datetime import date

from pydantic import BaseModel, Field

from profiles.enums import Gender, MilitaryService, LanguageLevel, MaritalStatus, Platform, SkillLevel
from locations.enums import LocationType
from common.enums import EducationLevel, ContractType


class ParsedEducation(BaseModel):
    """DTO for education information extracted from resume."""
    school: str = Field(..., description="Name of the educational institution")
    degree: Literal[
        EducationLevel.HIGH_SCHOOL.value,
        EducationLevel.BACHELOR.value,
        EducationLevel.MASTER.value,
        EducationLevel.DOCTORATE.value,
        EducationLevel.OTHER.value,
    ] = Field(..., description="Level of education/degree obtained")
    grade: Optional[str] = Field(None, description="GPA or grade achieved")
    field_of_study: str = Field(..., description="Major or field of study")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format, null if still studying")
    description: str = Field("", description="Additional description or achievements")


class ParsedExperience(BaseModel):
    """DTO for work experience information extracted from resume."""
    company: str = Field(..., description="Name of the company or organization")
    title: str = Field(..., description="Job title or position")
    location: str = Field(..., description="Location where the job was performed")
    location_type: Literal[
        LocationType.ON_SITE.value,
        LocationType.REMOTE.value,
        LocationType.HYBRID.value,
    ] = Field(..., description="Type of work location arrangement")
    contract_type: Literal[
        ContractType.FULL_TIME.value,
        ContractType.PART_TIME.value,
        ContractType.CONTRACT.value,
        ContractType.VOLUNTEER.value,
        ContractType.OTHER.value,
    ] = Field(..., description="Type of employment contract")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format, null if currently employed")
    description: str = Field("", description="Job responsibilities and achievements")


class ParsedSkill(BaseModel):
    """DTO for skill information extracted from resume."""
    name: str = Field(..., description="Name of the skill")
    level: Literal[
        SkillLevel.BEGINNER.value,
        SkillLevel.INTERMEDIATE.value,
        SkillLevel.ADVANCED.value,
        SkillLevel.EXPERT.value,
    ] = Field(..., description="Proficiency level of the skill")


class ParsedLanguage(BaseModel):
    """DTO for language proficiency information extracted from resume."""
    name: str = Field(..., description="Name of the language")
    level: Literal[
        LanguageLevel.BEGINNER.value,
        LanguageLevel.INTERMEDIATE.value,
        LanguageLevel.ADVANCED.value,
        LanguageLevel.NATIVE.value,
    ] = Field(..., description="Proficiency level in the language")


class ParsedCertification(BaseModel):
    """DTO for certification information extracted from resume."""
    title: str = Field(..., description="Title of the certification")
    description: str = Field("", description="Description of the certification")
    issued_by: str = Field(..., description="Organization that issued the certification")
    issued_date: str = Field(..., description="Date issued in YYYY-MM-DD format")
    expiration_date: Optional[str] = Field(None, description="Expiration date in YYYY-MM-DD format, null if no expiration")
    url: Optional[str] = Field(None, description="URL to verify the certification")
    reference_id: Optional[str] = Field(None, description="Certificate ID or reference number")


class ParsedProject(BaseModel):
    """DTO for project information extracted from resume."""
    name: str = Field(..., description="Name of the project")
    description: str = Field("", description="Description of the project and contributions")
    url: Optional[str] = Field(None, description="URL to the project (e.g., GitHub, portfolio)")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format, null if ongoing")


class ParsedSocialMedia(BaseModel):
    """DTO for social media profile information extracted from resume."""
    platform: Literal[
        Platform.LINKEDIN.value,
        Platform.X.value,
        Platform.INSTAGRAM.value,
        Platform.FACEBOOK.value,
        Platform.YOUTUBE.value,
        Platform.TIKTOK.value,
        Platform.OTHER.value,
    ] = Field(..., description="Social media platform name")
    url: str = Field(..., description="URL to the social media profile")


class ParsedAchievement(BaseModel):
    """DTO for achievement information extracted from resume."""
    name: str = Field(..., description="Title or name of the achievement")
    description: str = Field("", description="Description of the achievement")


class ParsedActivity(BaseModel):
    """DTO for activity/volunteer work information extracted from resume."""
    name: str = Field(..., description="Name of the activity or organization")
    description: str = Field("", description="Description of involvement and contributions")


class ParsedInterest(BaseModel):
    """DTO for interest/hobby information extracted from resume."""
    name: str = Field(..., description="Name of the interest or hobby")
    description: str = Field("", description="Additional description")


class ParsedResearch(BaseModel):
    """DTO for research/publication information extracted from resume."""
    title: str = Field(..., description="Title of the research or publication")
    description: str = Field("", description="Abstract or description of the research")


class ParsedRecommendation(BaseModel):
    """DTO for recommendation/reference information extracted from resume."""
    name: str = Field(..., description="Name of the reference person")
    email: Optional[str] = Field(None, description="Email address of the reference")
    phone_number: Optional[str] = Field(None, description="Phone number of the reference")
    message: str = Field("", description="Recommendation message or relationship description")


class ParsedUserInfo(BaseModel):
    """DTO for basic user information extracted from resume."""
    first_name: str = Field(..., description="First name of the person")
    last_name: str = Field(..., description="Last name of the person")
    email: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number in format 09xxxxxxxxx for Iranian numbers")


class ParsedProfileInfo(BaseModel):
    """DTO for profile information extracted from resume."""
    about: str = Field("", description="Professional summary or about section")
    birth_date: Optional[str] = Field(None, description="Birth date in YYYY-MM-DD format")
    gender: Optional[Literal[
        Gender.MALE.value,
        Gender.FEMALE.value,
    ]] = Field(None, description="Gender")
    military_service: Optional[Literal[
        MilitaryService.COMPLETED.value,
        MilitaryService.PENDING.value,
        MilitaryService.NOT_REQUIRED.value,
    ]] = Field(None, description="Military service status")
    marital_status: Optional[Literal[
        MaritalStatus.SINGLE.value,
        MaritalStatus.MARRIED.value,
    ]] = Field(None, description="Marital status")
    location: Optional[str] = Field(None, description="Current location/city of residence")
    description: str = Field("", description="Additional description or bio")


class ParsedResume(BaseModel):
    """Complete DTO for all information extracted from a resume."""
    user_info: ParsedUserInfo = Field(..., description="Basic user identification information")
    profile_info: ParsedProfileInfo = Field(..., description="Profile details and personal information")
    educations: List[ParsedEducation] = Field(default_factory=list, description="List of educational background")
    experiences: List[ParsedExperience] = Field(default_factory=list, description="List of work experiences")
    skills: List[ParsedSkill] = Field(default_factory=list, description="List of skills")
    languages: List[ParsedLanguage] = Field(default_factory=list, description="List of language proficiencies")
    certifications: List[ParsedCertification] = Field(default_factory=list, description="List of certifications")
    projects: List[ParsedProject] = Field(default_factory=list, description="List of projects")
    social_media: List[ParsedSocialMedia] = Field(default_factory=list, description="List of social media profiles")
    achievements: List[ParsedAchievement] = Field(default_factory=list, description="List of achievements")
    activities: List[ParsedActivity] = Field(default_factory=list, description="List of activities and volunteer work")
    interests: List[ParsedInterest] = Field(default_factory=list, description="List of interests and hobbies")
    research: List[ParsedResearch] = Field(default_factory=list, description="List of research and publications")
    recommendations: List[ParsedRecommendation] = Field(default_factory=list, description="List of recommendations/references")
    ai_summary: str = Field("", description="AI-generated summary of the entire resume")
