from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("PackReady", {"fields": ("role", "contact_number", "profile_photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("PackReady", {"fields": ("email", "role", "contact_number")}),
    )
    list_display = ("username", "email", "role", "is_staff")





    