from django.contrib import admin

from companies.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'page', 'image']
    search_fields = ['name', 'description', 'page']
    ordering = ['-created_at']
