from django.contrib import admin
from .models import DemoVideo, NewsletterSubscriber, Contact

@admin.register(DemoVideo)
class DemoVideoAdmin(admin.ModelAdmin):
    list_display = ("title","is_active","created_at")

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at", "is_active")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("full_name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("Contact Information", {
            "fields": ("full_name", "email", "phone", "company")
        }),
        ("Message", {
            "fields": ("subject", "message")
        }),
        ("Status", {
            "fields": ("is_read", "created_at")
        }),
    )