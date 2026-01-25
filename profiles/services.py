import json
import logging
import io
from typing import Optional, Dict, Any
from datetime import datetime

from django.conf import settings
from django.db import transaction
from pydantic import BaseModel, Field, ConfigDict
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage
from langfuse.langchain import CallbackHandler

from accounts.models import User
from profiles.models import (
    Profile, Education, Experience, Skill, Language,
    Certification, Project, Recommendation, SocialMedia,
    Achievement, Activity, Interest, Research, ResumeUpload
)
from profiles.dto import ParsedResume
from locations.services import LocationService
from common.enums import ProcessStatus


logger = logging.getLogger(__name__)


RESUME_PARSER_SYSTEM_PROMPT = """
# Role
You are an expert resume parser that extracts structured information from resume documents.

# Instructions
You will receive the raw text content extracted from a resume file.
Your task is to parse this content and extract all relevant information into a structured format.

# Critical Requirements
- ALL text output MUST be in English only, regardless of input language
- If input contains non-English text, translate it to English in your output
- Text fields can be null/None if truly missing, but prefer empty string "" for blank text
- Never include null bytes (\\x00, \\0, NUL) or other control characters in string values
- All string values must be valid UTF-8 text
- Dates must be in YYYY-MM-DD format. If only year is available, use YYYY-01-01. If year and month are available, use YYYY-MM-01.
- If a date cannot be determined, make a reasonable estimate based on context
- Phone numbers for Iranian candidates should be in format 09xxxxxxxxx

# Guidelines
- Extract as much information as possible from the resume
- Infer skill levels based on years of experience and context
- Infer language proficiency from explicit statements or context
- Map education degrees to the closest matching level
- Map contract types and location types to the closest matching value
- Generate a comprehensive AI summary that captures the candidate's key qualifications
"""

RESUME_PARSER_USER_PROMPT = """
# Resume Content
{resume_text}

# Instructions
Parse this resume and extract all information into the structured format.
Translate any non-English content to English.
Ensure all dates are in YYYY-MM-DD format.
"""


class ResumeParserService:
    """
    Service for extracting text from resume files and parsing them into structured data using AI.
    """
    
    def __init__(self, llm_model: str = "gpt-5-mini"):
        self.llm_model = llm_model
        
    def extract_text_from_file(self, file) -> str:
        """
        Extract text content from a resume file (PDF or DOCX).
        
        Args:
            file: Django file object
            
        Returns:
            Extracted text content as a string
        """
        filename = file.name.lower()
        file_content = file.read()
        
        if filename.endswith('.pdf'):
            return self._extract_from_pdf(file_content)
        elif filename.endswith('.docx'):
            return self._extract_from_docx(file_content)
        elif filename.endswith('.doc'):
            raise ValueError("Legacy .doc format is not supported. Please convert to .docx or .pdf")
        elif filename.endswith('.txt'):
            return file_content.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file content."""
        try:
            import pypdf
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        except ImportError:
            raise ImportError("pypdf is required for PDF parsing. Install it with: pip install pypdf")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {e}")
    
    def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file content."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_content))
            text_parts = []
            for paragraph in doc.paragraphs:
                text_parts.append(paragraph.text)
            # Also extract from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text_parts.append(cell.text)
            return "\n".join(text_parts)
        except ImportError:
            raise ImportError("python-docx is required for DOCX parsing. Install it with: pip install python-docx")
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise ValueError(f"Failed to extract text from DOCX: {e}")
    
    def parse_resume_text(self, resume_text: str) -> ParsedResume:
        """
        Parse extracted resume text into structured data using AI.
        
        Args:
            resume_text: Raw text extracted from resume file
            
        Returns:
            ParsedResume object with structured data
        """
        class ParserResult(BaseModel):
            model_config = ConfigDict(extra="forbid")
            parsed_resume: ParsedResume = Field(..., description="The parsed resume data")
        
        client = ChatOpenAI(
            **settings.LLM_SETTINGS["default"],
            model=self.llm_model,
            reasoning={"effort": "high", "summary": "auto"}
        ).with_structured_output(ParserResult, include_raw=True)
        
        langfuse_handler = CallbackHandler()
        
        resp = client.invoke(
            [
                SystemMessage(content=RESUME_PARSER_SYSTEM_PROMPT),
                HumanMessage(content=RESUME_PARSER_USER_PROMPT.format(resume_text=resume_text)),
            ],
            config={"callbacks": [langfuse_handler], "tags": ["resume-parser"]}
        )
        
        return resp["parsed"].parsed_resume
    
    def parse_resume_file(self, file) -> tuple[str, ParsedResume]:
        """
        Extract text from a resume file and parse it into structured data.
        
        Args:
            file: Django file object
            
        Returns:
            Tuple of (raw_text, ParsedResume)
        """
        raw_text = self.extract_text_from_file(file)
        parsed_resume = self.parse_resume_text(raw_text)
        return raw_text, parsed_resume


class ResumeToProfileService:
    """
    Service for converting parsed resume data into Profile and related Django models.
    """
    
    def __init__(self, location_service: Optional[LocationService] = None):
        self.location_service = location_service or LocationService()
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse a date string in YYYY-MM-DD format."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Could not parse date: {date_str}")
            return None
    
    def _generate_phone_number(self) -> str:
        """Generate a unique phone number for users without one."""
        import random
        while True:
            phone = f"09{random.randint(100000000, 999999999)}"
            if not User.objects.filter(phone_number=phone).exists():
                return phone
    
    @transaction.atomic
    def create_profile_from_parsed_resume(
        self, 
        parsed_resume: ParsedResume,
        resume_upload: Optional[ResumeUpload] = None
    ) -> Profile:
        """
        Create a User, Profile, and all related models from parsed resume data.
        
        Args:
            parsed_resume: ParsedResume object with structured data
            resume_upload: Optional ResumeUpload instance to link to the profile
            
        Returns:
            Created Profile instance
        """
        user_info = parsed_resume.user_info
        profile_info = parsed_resume.profile_info
        
        # Create or get user
        phone_number = user_info.phone_number
        if not phone_number or not phone_number.startswith("09") or len(phone_number) != 11:
            phone_number = self._generate_phone_number()
        
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                "first_name": user_info.first_name,
                "last_name": user_info.last_name,
                "email": user_info.email or "",
            }
        )
        
        if not created:
            # Update user info if user already exists
            user.first_name = user_info.first_name
            user.last_name = user_info.last_name
            if user_info.email:
                user.email = user_info.email
            user.save()
        
        # Create or update profile
        profile, profile_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                "about": profile_info.about,
                "birth_date": self._parse_date(profile_info.birth_date),
                "gender": profile_info.gender,
                "military_service": profile_info.military_service,
                "marital_status": profile_info.marital_status,
                "description": profile_info.description,
                "ai_summary": parsed_resume.ai_summary,
            }
        )
        
        if not profile_created:
            # Update profile info
            profile.about = profile_info.about
            profile.birth_date = self._parse_date(profile_info.birth_date)
            profile.gender = profile_info.gender
            profile.military_service = profile_info.military_service
            profile.marital_status = profile_info.marital_status
            profile.description = profile_info.description
            profile.ai_summary = parsed_resume.ai_summary
            profile.save()
            
            # Clear existing related objects to replace with new data
            profile.educations.all().delete()
            profile.experiences.all().delete()
            profile.skills.all().delete()
            profile.languages.all().delete()
            profile.certifications.all().delete()
            profile.projects.all().delete()
            profile.social_media.all().delete()
            profile.achievements.all().delete()
            profile.activities.all().delete()
            profile.interests.all().delete()
            profile.research.all().delete()
            profile.recommendations.all().delete()
        
        # Add location if specified
        if profile_info.location:
            try:
                locations = self.location_service.get_or_create_locations([profile_info.location])
                if locations:
                    profile.location.set(locations)
            except Exception as e:
                logger.warning(f"Could not set location: {e}")
        
        # Create educations
        for edu in parsed_resume.educations:
            Education.objects.create(
                profile=profile,
                school=edu.school,
                degree=edu.degree,
                grade=edu.grade,
                field_of_study=edu.field_of_study,
                start_date=self._parse_date(edu.start_date),
                end_date=self._parse_date(edu.end_date),
                description=edu.description,
            )
        
        # Create experiences
        for exp in parsed_resume.experiences:
            Experience.objects.create(
                profile=profile,
                company=exp.company,
                title=exp.title,
                location=exp.location,
                location_type=exp.location_type,
                contract_type=exp.contract_type,
                start_date=self._parse_date(exp.start_date),
                end_date=self._parse_date(exp.end_date),
                description=exp.description,
            )
        
        # Create skills
        for skill in parsed_resume.skills:
            Skill.objects.create(
                profile=profile,
                name=skill.name,
                level=skill.level,
            )
        
        # Create languages
        for lang in parsed_resume.languages:
            Language.objects.create(
                profile=profile,
                name=lang.name,
                level=lang.level,
            )
        
        # Create certifications
        for cert in parsed_resume.certifications:
            Certification.objects.create(
                profile=profile,
                title=cert.title,
                description=cert.description,
                issued_by=cert.issued_by,
                issued_date=self._parse_date(cert.issued_date),
                expiration_date=self._parse_date(cert.expiration_date),
                url=cert.url,
                reference_id=cert.reference_id,
            )
        
        # Create projects
        for proj in parsed_resume.projects:
            Project.objects.create(
                profile=profile,
                name=proj.name,
                description=proj.description,
                url=proj.url or "",
                start_date=self._parse_date(proj.start_date),
                end_date=self._parse_date(proj.end_date),
            )
        
        # Create social media
        for sm in parsed_resume.social_media:
            SocialMedia.objects.create(
                profile=profile,
                platform=sm.platform,
                url=sm.url,
            )
        
        # Create achievements
        for ach in parsed_resume.achievements:
            Achievement.objects.create(
                profile=profile,
                name=ach.name,
                description=ach.description,
            )
        
        # Create activities
        for act in parsed_resume.activities:
            Activity.objects.create(
                profile=profile,
                name=act.name,
                description=act.description,
            )
        
        # Create interests
        for interest in parsed_resume.interests:
            Interest.objects.create(
                profile=profile,
                name=interest.name,
                description=interest.description,
            )
        
        # Create research
        for res in parsed_resume.research:
            Research.objects.create(
                profile=profile,
                title=res.title,
                description=res.description,
            )
        
        # Create recommendations
        for rec in parsed_resume.recommendations:
            if rec.email or rec.phone_number:  # Only create if contact info is available
                Recommendation.objects.create(
                    profile=profile,
                    name=rec.name,
                    email=rec.email or "",
                    phone_number=rec.phone_number or "",
                    message=rec.message,
                )
        
        # Link resume upload to profile
        if resume_upload:
            resume_upload.profile = profile
            resume_upload.save()
        
        return profile


class ResumeConversionService:
    """
    High-level service that orchestrates the entire resume-to-profile conversion process.
    """
    
    def __init__(
        self,
        parser_service: Optional[ResumeParserService] = None,
        profile_service: Optional[ResumeToProfileService] = None
    ):
        self.parser_service = parser_service or ResumeParserService()
        self.profile_service = profile_service or ResumeToProfileService()
    
    def process_resume_upload(self, resume_upload: ResumeUpload) -> Profile:
        """
        Process a ResumeUpload instance: extract text, parse it, and create a profile.
        
        Args:
            resume_upload: ResumeUpload instance to process
            
        Returns:
            Created Profile instance
            
        Raises:
            Exception: If processing fails
        """
        try:
            # Update status to processing
            resume_upload.process_status = ProcessStatus.PROCESSING.value
            resume_upload.save()
            
            # Extract and parse resume
            resume_upload.file.seek(0)  # Reset file pointer
            raw_text, parsed_resume = self.parser_service.parse_resume_file(resume_upload.file)
            
            # Store raw and parsed data
            resume_upload.raw_data = {"text": raw_text}
            resume_upload.parsed_data = parsed_resume.model_dump()
            resume_upload.save()
            
            # Create profile from parsed data
            profile = self.profile_service.create_profile_from_parsed_resume(
                parsed_resume,
                resume_upload=resume_upload
            )
            
            # Update status to finished
            resume_upload.process_status = ProcessStatus.FINISHED.value
            resume_upload.save()
            
            logger.info(f"Successfully processed resume upload {resume_upload.id}, created profile {profile.id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to process resume upload {resume_upload.id}: {e}")
            resume_upload.process_status = ProcessStatus.FAILED.value
            resume_upload.error_message = str(e)
            resume_upload.save()
            raise
