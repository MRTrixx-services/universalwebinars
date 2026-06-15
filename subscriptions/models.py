from django.db import models
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class SubscriptionPlan(models.Model):
    DURATION_CHOICES = (
        (6, "6 Months"),
        (12, "1 Year"),
    )

    name = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField(choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    paypal_plan_id = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ["duration_months"]

    def __str__(self):
        return f"{self.name} – ${self.price}"


class UserSubscription(models.Model):

    STATUS = (
        ("ACTIVE","Active"),
        ("EXPIRED","Expired"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    payment_id = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS, default="ACTIVE")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} – {self.plan}"
    
    @property
    def days_left(self):
        now = timezone.now()

        if self.end_date <= now:
            return 0

        return (self.end_date.date() - now.date()).days
    
    
class SubscriptionPayment(models.Model):

    STATUS = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription_payments"
    )

    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)

    paypal_id = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SubscriptionPayment #{self.id} - {self.user.email}"