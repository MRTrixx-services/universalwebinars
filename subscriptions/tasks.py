from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import UserSubscription
from .email_utils import send_subscription_expiry_email


@shared_task
def send_subscription_expiry_reminders():

    now = timezone.now()
    reminder_date = now + timedelta(days=3)

    subs = UserSubscription.objects.filter(
        status="ACTIVE",
        end_date__date=reminder_date.date()
    )

    for sub in subs:
        send_subscription_expiry_email(sub)