from django.contrib import admin

from profiles.models import Profile, Education, Experience, Skill, Language, Certification, Project, Recommendation, SocialMedia, Achievement, Activity, Interest, Research, Preferences


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0

class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0

class RecommendationInline(admin.TabularInline):
    model = Recommendation
    extra = 0

class SocialMediaInline(admin.TabularInline):
    model = SocialMedia
    extra = 0

class AchievementInline(admin.TabularInline):
    model = Achievement
    extra = 0

class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0

class InterestInline(admin.TabularInline):
    model = Interest
    extra = 0

class ResearchInline(admin.TabularInline):
    model = Research
    extra = 0

class PreferencesInline(admin.StackedInline):
    model = Preferences
    extra = 0

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'about', 'birth_date', 'gender', 'military_service', 'marital_status']
    search_fields = ['user__phone_number', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-created_at']
    inlines = [
        EducationInline, ExperienceInline, SkillInline, LanguageInline, CertificationInline, ProjectInline,
        RecommendationInline, SocialMediaInline, AchievementInline, ActivityInline, InterestInline, ResearchInline, PreferencesInline
    ]
