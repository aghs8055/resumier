from django.contrib import admin

from jobs.models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "company",
        "contract_type",
        "experience_level",
        "is_active",
    ]
    search_fields = [
        "title",
        "company__name",
        "location__name",
        "contract_type",
        "experience_level",
        "category",
    ]
    list_filter = [
        "contract_type",
        "experience_level",
        "category",
        "military_service",
        "gender",
        "currency",
        "minimum_salary",
        "gender",
        "minimum_experience_years",
        "minimum_education_level",
    ]
    ordering = ["-created_at"]
    list_editable = ["is_active"]
