from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from profiles.models import (
    Profile, Education, Experience, Skill, Language, Certification, 
    Project, Recommendation, SocialMedia, Achievement, Activity, 
    Interest, Research, Preferences, ResumeUpload
)
from common.enums import ProcessStatus


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


@admin.register(ResumeUpload)
class ResumeUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'process_status_display', 'profile_link', 'created_at', 'updated_at']
    list_filter = ['process_status', 'created_at']
    search_fields = ['id', 'file']
    readonly_fields = ['process_status', 'raw_data', 'parsed_data', 'error_message', 'profile', 'created_at', 'updated_at']
    ordering = ['-created_at']
    actions = ['process_resumes', 'queue_for_processing', 'reset_failed_resumes']
    
    fieldsets = (
        ('Upload', {
            'fields': ('file',),
            'description': 'Upload a resume file (PDF, DOCX, or TXT format). The file will be processed to create a profile.'
        }),
        ('Processing Status', {
            'fields': ('process_status', 'error_message', 'profile'),
            'classes': ('collapse',),
        }),
        ('Extracted Data', {
            'fields': ('raw_data', 'parsed_data'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def file_name(self, obj):
        """Display the file name."""
        if obj.file:
            return obj.file.name.split('/')[-1]
        return '-'
    file_name.short_description = 'File'
    
    def process_status_display(self, obj):
        """Display the process status with color coding."""
        status_colors = {
            ProcessStatus.PENDING.value: '#ffc107',  # Yellow
            ProcessStatus.PROCESSING.value: '#17a2b8',  # Blue
            ProcessStatus.FINISHED.value: '#28a745',  # Green
            ProcessStatus.FAILED.value: '#dc3545',  # Red
        }
        color = status_colors.get(obj.process_status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.process_status
        )
    process_status_display.short_description = 'Status'
    
    def profile_link(self, obj):
        """Display a link to the created profile."""
        if obj.profile:
            from django.urls import reverse
            url = reverse('admin:profiles_profile_change', args=[obj.profile.id])
            return format_html('<a href="{}">{}</a>', url, obj.profile)
        return '-'
    profile_link.short_description = 'Profile'
    
    def save_model(self, request, obj, form, change):
        """Save the model and optionally trigger processing."""
        if not change:  # New upload
            obj.process_status = ProcessStatus.PENDING.value
        super().save_model(request, obj, form, change)
        
        # Show message to user
        if not change:
            messages.info(
                request, 
                f'Resume uploaded successfully. Use the "Process selected resumes" action to convert it to a profile, '
                f'or wait for the background task to process it automatically.'
            )
    
    @admin.action(description='Process selected resumes immediately')
    def process_resumes(self, request, queryset):
        """Admin action to process selected resume uploads immediately."""
        from profiles.services import ResumeConversionService
        
        conversion_service = ResumeConversionService()
        success_count = 0
        error_count = 0
        
        for resume_upload in queryset.filter(process_status__in=[
            ProcessStatus.PENDING.value, 
            ProcessStatus.FAILED.value
        ]):
            try:
                conversion_service.process_resume_upload(resume_upload)
                success_count += 1
            except Exception as e:
                error_count += 1
                messages.error(request, f'Failed to process resume {resume_upload.id}: {str(e)}')
        
        if success_count:
            messages.success(request, f'Successfully processed {success_count} resume(s).')
        if error_count:
            messages.warning(request, f'Failed to process {error_count} resume(s). Check the error messages above.')
    
    @admin.action(description='Queue selected resumes for background processing')
    def queue_for_processing(self, request, queryset):
        """Admin action to queue selected resume uploads for background processing."""
        from profiles.tasks import process_resume_upload_task
        
        queued_count = 0
        for resume_upload in queryset.filter(process_status__in=[
            ProcessStatus.PENDING.value, 
            ProcessStatus.FAILED.value
        ]):
            process_resume_upload_task.delay(resume_upload.id)
            queued_count += 1
        
        if queued_count:
            messages.success(request, f'Queued {queued_count} resume(s) for background processing.')
        else:
            messages.info(request, 'No eligible resumes to queue (only pending or failed resumes can be queued).')
    
    @admin.action(description='Reset failed resumes to pending')
    def reset_failed_resumes(self, request, queryset):
        """Admin action to reset failed resume uploads to pending status."""
        updated = queryset.filter(process_status=ProcessStatus.FAILED.value).update(
            process_status=ProcessStatus.PENDING.value,
            error_message=None
        )
        if updated:
            messages.success(request, f'Reset {updated} failed resume(s) to pending status.')
        else:
            messages.info(request, 'No failed resumes selected.')
