from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .utils import generate_invoice_pdf


def send_invoice_email(order):

    pdf_file = generate_invoice_pdf(order)

    subject = f"Payment Confirmation – Invoice {order.invoice_number}"

    html_message = render_to_string(
        "emails/order_invoice_email.html",
        {"order": order}
    )

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.user.email],
    )

    email.content_subtype = "html"

    email.attach(
        f"Invoice_{order.invoice_number}.pdf",
        pdf_file.getvalue(),
        "application/pdf"
    )

    email.send()