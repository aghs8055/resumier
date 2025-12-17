from django.contrib import admin

from locations.models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "level"]
    search_fields = ["name", "level"]
    ordering = ["-created_at"]