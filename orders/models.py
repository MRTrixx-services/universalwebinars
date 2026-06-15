from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import datetime


class Order(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    ]

    order_number = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )

    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    payment_id = models.CharField(max_length=200, blank=True, null=True)
    gateway_transaction_id = models.CharField(max_length=200, blank=True, null=True)

    gateway_order_id = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
    
        is_new = not self.id

        if is_new:
            # Remove force_insert so second save won't crash
            kwargs.pop("force_insert", None)
            super().save(*args, **kwargs)  # Get the ID first

        if not self.order_number:
            self.order_number = f"WFS{self.id:04d}"

        if self.status == "PAID" and not self.invoice_number:
            year = self.created_at.year if self.created_at else datetime.now().year
            self.invoice_number = f"INV-{year}-{self.id:04d}"

        # Always update (never insert again)
        kwargs.pop("force_insert", None)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.user.email}"
    

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)

    webinar_title = models.CharField(max_length=255)
    webinar_ref_id = models.CharField(max_length=50)

    variant = models.CharField(max_length=20)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    instructor_name = models.CharField(max_length=255, null=True, blank=True)
    category_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.webinar_title



from django.db import models


class PaymentLog(models.Model):

    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="payment_logs"
    )

    event = models.CharField(max_length=100)

    request_data = models.JSONField(blank=True, null=True)

    response_data = models.JSONField(blank=True, null=True)

    status = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.event}"