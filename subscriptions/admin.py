from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db.models import Q
from .models import SubscriptionPlan, UserSubscription, SubscriptionPayment

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "duration_months",
        "price",
        "status_badge",
        "popularity_badge",
        "created_at",
    )
    list_filter = ("is_active", "is_popular", "duration_months")
    search_fields = ("name",)
    ordering = ("duration_months",)
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("Plan Information", {
            "fields": ("name", "duration_months", "price")
        }),
        ("Status", {
            "fields": ("is_active", "is_popular")
        }),
        ("PayPal Integration", {
            "fields": ("paypal_plan_id",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                '✓ Active'
            )

        return format_html(
            '<span style="color: red; font-weight: bold;">{}</span>',
            '✗ Inactive'
        )
    status_badge.short_description = "Status"
    
    def popularity_badge(self, obj):
        if obj.is_popular:
            return format_html(
                '<span style="color: #ff9800; font-weight: bold;">{}</span>',
                '⭐ Popular'
            )

        return format_html(
            '<span style="color: #ccc;">{}</span>',
            '—'
        )
    popularity_badge.short_description = "Popular"

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user_name",
        "user_email",
        "plan",
        "status_badge",
        "subscription_period",
        "days_remaining_badge",
        "created_at",
    )
    
    list_filter = ("status", "plan", "start_date", "end_date")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "payment_id")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "days_remaining_display")
    
    fieldsets = (
        ("User Information", {
            "fields": ("user",)
        }),
        ("Subscription Details", {
            "fields": ("plan", "start_date", "end_date", "status")
        }),
        ("Payment Information", {
            "fields": ("payment_id",)
        }),
        ("Timestamps & Info", {
            "fields": ("created_at", "days_remaining_display"),
            "classes": ("collapse",)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = "User Name"
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"
    
    def status_badge(self, obj):
        if obj.status == "ACTIVE":
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Expired</span>')
    status_badge.short_description = "Status"
    
    def subscription_period(self, obj):
        start = obj.start_date.strftime('%d %b %Y')
        end = obj.end_date.strftime('%d %b %Y')
        return f"{start} → {end}"
    subscription_period.short_description = "Period"
    
    def days_remaining_badge(self, obj):
        days = self._calculate_days_remaining(obj)
        if days > 30:
            color = "green"
        elif days > 7:
            color = "orange"
        else:
            color = "red"
        return format_html(
    '<span style="color: {}; font-weight: bold;">{} days</span>',
    color,
    days
)
    days_remaining_badge.short_description = "Days Left"
    
    def days_remaining_display(self, obj):
        return self._calculate_days_remaining(obj)
    days_remaining_display.short_description = "Days Remaining"
    
    def _calculate_days_remaining(self, obj):
        if obj.end_date:
            diff = obj.end_date - timezone.now()
            return max(diff.days, 0)
        return 0

@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_email",
        "plan",
        "status_badge",
        "amount",
        "paypal_id",
        "created_at",
    )
    
    list_filter = ("status", "plan", "created_at")
    search_fields = ("user__username", "user__email", "paypal_id")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "user", "plan", "paypal_id")
    
    fieldsets = (
        ("User & Plan", {
            "fields": ("user", "plan")
        }),
        ("Payment Details", {
            "fields": ("status", "paypal_id")
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"
    
    def status_badge(self, obj):
        colors = {
            "PENDING": "orange",
            "PAID": "green",
            "FAILED": "red"
        }
        color = colors.get(obj.status, "gray")
        return format_html(
    '<span style="color: {}; font-weight: bold;">{}</span>',
    color,
    obj.get_status_display()
)
    status_badge.short_description = "Status"
    
    def amount(self, obj):
        return f"${obj.plan.price}"
    amount.short_description = "Amount"