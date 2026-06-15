from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser
    """

    model = CustomUser
    ordering = ("-created_at",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "company",
        "country",
        "phone_number",
        "is_verified",
        "is_staff",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "is_verified",
        "country",
        "created_at",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "company",
        "phone_number",
    )

    readonly_fields = ("created_at", "updated_at")

    # 🔹 Fieldsets for Edit Page
    fieldsets = (
        (_("Authentication"), {
            "fields": ("email", "password")
        }),
        (_("Personal Info"), {
            "fields": (
                "first_name",
                "last_name",
                "company",
                "country",
                "phone_number",
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Status"), {
            "fields": (
                "is_verified",
                "is_profile_completed",
            )
        }),
        (_("Important Dates"), {
            "fields": ("last_login", "created_at", "updated_at")
        }),
    )

    # 🔹 Add User Page Layout
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )
