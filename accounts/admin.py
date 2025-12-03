from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['phone_number', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    list_editable = ['is_staff', 'is_active']
