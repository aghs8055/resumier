from django.contrib import admin

from companies.models import Company, Perk


@admin.register(Perk)
class PerkAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'page', 'image']
    search_fields = ['name', 'description', 'page']
    ordering = ['-created_at']
