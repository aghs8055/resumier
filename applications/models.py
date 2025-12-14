from django.db import models

from applications.storages import ResumeStorage
from jobs.models import Opportunity
from profiles.models import Profile
from common.enums import ProcessStatus
from common.models import TimedModel


class Application(TimedModel):
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='applications', null=True)
    job = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, related_name='applications', null=True)
    resume = models.FileField(upload_to='', storage=ResumeStorage())
    cover_letter = models.TextField(blank=True)
    process_status = models.CharField(max_length=32, choices=ProcessStatus.choices(), null=False, blank=False)
    
    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
