from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_subscription_email(subscription):

    subject = "Subscription Activated – dailyrespond"

    html_message = render_to_string(
        "emails/subscription_confirmation.html",
        {
            "subscription": subscription,
            "user": subscription.user,
            "plan": subscription.plan,
        }
    )

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscription.user.email],
    )

    email.content_subtype = "html"
    email.send()


# 🔔 Expiry reminder email
def send_subscription_expiry_email(subscription):

    subject = "Your dailyrespond Subscription Expires Soon"

    html_message = render_to_string(
        "emails/subscription_expiry_reminder.html",
        {
            "subscription": subscription,
            "user": subscription.user,
            "plan": subscription.plan,
        }
    )

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscription.user.email],
    )

    email.content_subtype = "html"
    email.send()