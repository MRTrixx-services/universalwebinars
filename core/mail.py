from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    subject = "Welcome to dailyrespond 🚀"

    html_content = render_to_string("emails/welcome.html", {
        "user": user
    })

    msg = EmailMultiAlternatives(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send(fail_silently=True)
    except Exception as e:
        print("Welcome email error:", e)