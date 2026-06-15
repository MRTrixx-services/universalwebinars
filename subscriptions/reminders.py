# subscriptions/reminders.py
from django.utils import timezone
from datetime import timedelta
from .models import UserSubscription
from .email_utils import send_subscription_expiry_email


def send_expiry_reminders():

    now = timezone.now()
    reminder_date = now + timedelta(days=3)

    subs = UserSubscription.objects.filter(
        status="ACTIVE",
        end_date__date=reminder_date.date()
    )

    for sub in subs:
        try:
            send_subscription_expiry_email(sub)
        except Exception as e:
            print(f"Reminder email failed for {sub.user.email}: {e}")