from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    fields = ("webinar_title", "variant", "price")
    readonly_fields = ("webinar_title", "variant", "price")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "order_date",
        "user_name",
        "user_email",
        "order_type",
        "item_titles",
        "subtotal",
        "total_amount",
        "payment_provider",
        "payment_id",
        "status",
    )

    inlines = [OrderItemInline]
    list_filter = ("status","created_at")
    search_fields = ("user__email","payment_id","id")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    # ===== helpers =====

    def order_date(self, obj):
        return obj.created_at
    order_date.short_description = "Order Date"

    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = "User Name"

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"

    def order_type(self, obj):
        first = obj.items.first()
        return first.variant if first else "-"
    order_type.short_description = "Order Type"

    def item_titles(self, obj):
        return ", ".join([i.webinar_title for i in obj.items.all()])
    item_titles.short_description = "Items" 

    

    def subtotal(self, obj):
        return sum(i.price for i in obj.items.all())
    subtotal.short_description = "Subtotal"

    def payment_provider(self, obj):
        return "PayPal" if obj.payment_id else "-"
    payment_provider.short_description = "Payment Provider"