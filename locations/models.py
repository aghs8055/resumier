from django.db import models

from locations.enums import LocationLevel


class Location(models.Model):
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=LocationLevel.choices())
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['-created_at']