from django.contrib import admin

from .models import (
    GlobalPricing,
    WebinarCategory,
    Instructor,
    LiveWebinar,
    WebinarPricing,
  
)

from integrations.models import ZoomMeeting


# -----------------------------
# GLOBAL PRICING
# -----------------------------
@admin.register(GlobalPricing)
class GlobalPricingAdmin(admin.ModelAdmin):

    list_display = (
        "live_single_price",
        "live_multi_price",
        "recorded_single_price",
        "recorded_multi_price",
        "combo_single_price",
        "combo_multi_price",
        "updated_at",
    )

    def has_add_permission(self, request):
        return not GlobalPricing.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if GlobalPricing.objects.exists():
            obj = GlobalPricing.objects.first()
            from django.shortcuts import redirect
            return redirect('admin:live_webinars_globalpricing_change', obj.id)

        return super().changelist_view(request, extra_context)


# -----------------------------
# BASIC REGISTRATIONS
# -----------------------------
@admin.register(WebinarCategory)
class WebinarCategoryAdmin(admin.ModelAdmin):

    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):

    list_display = ("name", "designation", "organization")
    search_fields = ("name", "designation", "organization")


# -----------------------------
# INLINE SECTIONS
# -----------------------------
class WebinarPricingInline(admin.StackedInline):
    model = WebinarPricing
    extra = 0
    max_num = 1




# -----------------------------
# ZOOM INLINE
# -----------------------------
class ZoomMeetingInline(admin.StackedInline):
    model = ZoomMeeting
    extra = 0
    max_num = 1
    readonly_fields = (
        "zoom_meeting_id",
        "topic",
        "join_url",
        "start_time",
        "duration",
    )


# -----------------------------
# MAIN LIVE WEBINAR ADMIN
# -----------------------------
@admin.register(LiveWebinar)
class LiveWebinarAdmin(admin.ModelAdmin):

    list_display = (
        "webinar_id",
        "title",
        "start_datetime",
        "status",
        "is_test",
    )

    list_filter = (
        "status",
        "is_test",
        "category",
    )

    search_fields = (
        "title",
        "webinar_id",
    )

    ordering = ("-start_datetime",)

    readonly_fields = (
        "webinar_id",
        "status",
        "created_at",
    )

    fieldsets = (
        ("Webinar Info", {
            "fields": (
                "webinar_id",
                "title",
                "category",
                "instructor",
                "is_test",
            )
        }),

        ("Schedule", {
            "fields": (
                "start_datetime",
                "duration_minutes",
            )
        }),

        ("Content", {
            "fields": (
                "description",
            )
        }),

        ("System", {
            "fields": (
                "status",
                "created_at",
            )
        }),
    )

    inlines = [
        ZoomMeetingInline,
        WebinarPricingInline,
        
    ]