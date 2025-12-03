from django.db import models
from django.contrib.postgres.fields import ArrayField

from accounts.models import User
from profiles.enums import Gender, MilitaryService, LanguageLevel, MaritalStatus, Platform, SkillLevel
from locations.models import Location
from locations.enums import LocationType
from common.enums import EducationLevel, ContractType


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    about = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=255, choices=Gender.choices(), null=True, blank=True)
    military_service = models.CharField(max_length=255, choices=MilitaryService.choices(), null=True, blank=True)
    marital_status = models.CharField(max_length=255, choices=MaritalStatus.choices(), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.phone_number

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, choices=EducationLevel.choices())
    grade = models.CharField(max_length=255, null=True, blank=True)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255, choices=LocationType.choices())
    contract_type = models.CharField(max_length=255, choices=ContractType.choices())
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'


class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=SkillLevel.choices())

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'


class Language(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=LanguageLevel.choices())

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'


class Certification(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    issued_by = models.CharField(max_length=255)
    issued_date = models.DateField()
    expiration_date = models.DateField(null=True)
    url = models.URLField(blank=True, null=True)
    reference_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'


class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class Recommendation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='recommendations')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'


class SocialMedia(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_media')
    platform = models.CharField(max_length=255, choices=Platform.choices())
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.platform

    class Meta:
        verbose_name = 'Social Media'
        verbose_name_plural = 'Social Media'


class Achievement(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='achievements')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'


class Activity(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'


class Interest(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='interests')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'
        

class Research(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='research')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Research'
        verbose_name_plural = 'Research'


class Preferences(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='preferences')
    location_type = ArrayField(models.CharField(max_length=255, choices=LocationType.choices()), null=True, blank=True)
    locations = models.ManyToManyField(Location, related_name='preferences')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.location_type

    class Meta:
        verbose_name = 'Preferences'
        verbose_name_plural = 'Preferences'
