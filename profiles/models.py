from django.db import models
from django.contrib.postgres.fields import ArrayField

from accounts.models import User
from profiles.enums import Gender, MilitaryService, LanguageLevel, MaritalStatus, Platform, SkillLevel
from locations.models import Location
from locations.enums import LocationType
from common.enums import EducationLevel, ContractType, ExperienceLevel, Currency, ProcessStatus
from profiles.storages import ResumeStorage
from common.models import TimedModel


class Profile(TimedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    about = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=255, choices=Gender.choices(), null=True, blank=True)
    military_service = models.CharField(max_length=255, choices=MilitaryService.choices(), null=True, blank=True)
    marital_status = models.CharField(max_length=255, choices=MaritalStatus.choices(), null=True, blank=True)
    location = models.ManyToManyField(Location, related_name='profiles')
    picture = models.ImageField(null=True, )
    description = models.TextField(null=True, blank=True)
    ai_summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.phone_number

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class Education(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, choices=EducationLevel.choices())
    grade = models.CharField(max_length=255, null=True, blank=True)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.school

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'


class Experience(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255, choices=LocationType.choices())
    contract_type = models.CharField(max_length=255, choices=ContractType.choices())
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'


class Skill(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=SkillLevel.choices())

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'


class Language(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=LanguageLevel.choices())

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'


class Certification(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    issued_by = models.CharField(max_length=255)
    issued_date = models.DateField()
    expiration_date = models.DateField(null=True)
    url = models.URLField(blank=True, null=True)
    reference_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'


class Project(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class Recommendation(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='recommendations')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'


class SocialMedia(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_media')
    platform = models.CharField(max_length=255, choices=Platform.choices())
    url = models.URLField()

    def __str__(self):
        return self.platform

    class Meta:
        verbose_name = 'Social Media'
        verbose_name_plural = 'Social Media'


class Achievement(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='achievements')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'


class Activity(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'


class Interest(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='interests')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'
        

class Research(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='research')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Research'
        verbose_name_plural = 'Research'


class Preferences(TimedModel):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='preferences')
    location_type = ArrayField(models.CharField(max_length=255, choices=LocationType.choices()), null=True, blank=True)
    locations = models.ManyToManyField(Location, related_name='preferences')
    minimum_experience_level = models.CharField(max_length=255, choices=ExperienceLevel.choices(), null=True, blank=True)
    maximum_experience_level = models.CharField(max_length=255, choices=ExperienceLevel.choices(), null=True, blank=True)
    minimum_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=255, choices=Currency.choices(), null=True, blank=True)
    languages = models.ManyToManyField(Language, related_name='preferences')

    class Meta:
        verbose_name = 'Preferences'
        verbose_name_plural = 'Preferences'


class ResumeFile(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='resume_files')
    file = models.FileField(upload_to='', storage=ResumeStorage())
    process_status = models.CharField(max_length=32, choices=ProcessStatus.choices())
    raw_data = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Resume File'
        verbose_name_plural = 'Resume Files'
