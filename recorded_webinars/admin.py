from django.contrib import admin
from .models import (
    RecordedWebinar,
    RecordedWebinarPricing,
    
)


# ---------------------------
# Inline Sections
# ---------------------------

class RecordedWebinarPricingInline(admin.StackedInline):
    model = RecordedWebinarPricing
    extra = 0
    max_num = 1


# ---------------------------
# Main Admin
# ---------------------------

@admin.register(RecordedWebinar)
class RecordedWebinarAdmin(admin.ModelAdmin):

    list_display = (
        "webinar_id",
        "title",
        "category",
        "instructor",
        "duration_minutes",
        "is_published",
        "created_at",
    )

    list_filter = (
        "is_published",
        "category",
        "instructor",
        "created_at",
    )

    search_fields = (
        "webinar_id",
        "title",
        "instructor__name",
    )

    readonly_fields = ("webinar_id", "created_at")

    fieldsets = (
        ("Webinar Info", {
            "fields": (
                "webinar_id",
                "title",
                "category",
                "instructor",
                "duration_minutes",
                "is_published",
            )
        }),

        ("Content", {
            "fields": (
                "description",
            )
        }),

        ("System", {
            "fields": (
                "created_at",
            )
        }),
    )

    inlines = [
        RecordedWebinarPricingInline,
    ]

    ordering = ("-created_at",)
