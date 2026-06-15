from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache

from .models import DemoVideo, NewsletterSubscriber, Contact
from live_webinars.models import LiveWebinar, Instructor
from recorded_webinars.models import RecordedWebinar
from subscriptions.models import SubscriptionPlan


def home(request):

    cache_key = "home_page_data"
    cached_data = cache.get(cache_key)

    if cached_data:
        return render(request, "home/index.html", cached_data)

    # Subscription Plans
    subscription_plans = list(
        SubscriptionPlan.objects
        .filter(is_active=True)
        .only(
            "id",
            "name",
            "price",
            "duration_months",
            "is_popular",
        )
        .order_by("duration_months")
    )

    # Instructors
    instructors = list(
        Instructor.objects
        .filter(photo__isnull=False)
        .exclude(photo="")
        .only(
            "id",
            "name",
            "designation",
            "organization",
            "photo",
        )
    )

    # Upcoming Webinars
    upcoming_webinars = list(
        LiveWebinar.objects
        .filter(start_datetime__gte=timezone.now())
        .exclude(status="ENDED")
        .select_related("instructor", "webinarpricing")
        .order_by("start_datetime")[:8]
    )

    context = {
        "subscription_plans": subscription_plans,
        "instructors": instructors,
        "upcoming_webinars": upcoming_webinars,
    }

    # cache for 5 mins
    cache.set(cache_key, context, 300)

    return render(request, "home/index.html", context)


def about_view(request):
    return render(request, "home/about.html")


def contact_view(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        company = request.POST.get("company", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        # Validation
        if not all([full_name, email, subject, message]):
            messages.error(
                request,
                "Please fill in all required fields."
            )
            return render(request, "home/contact.html")

        try:

            # Save contact
            Contact.objects.create(
                full_name=full_name,
                email=email,
                company=company,
                phone=phone,
                subject=subject,
                message=message
            )

            # Admin email
            admin_context = {
                "full_name": full_name,
                "email": email,
                "company": company,
                "phone": phone,
                "subject": subject,
                "message": message,
            }

            admin_html = render_to_string(
                "emails/contact_admin.html",
                admin_context
            )

            admin_msg = EmailMultiAlternatives(
                subject=f"New Contact Form Submission: {subject}",
                body="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.EMAIL_HOST_USER],
            )

            admin_msg.attach_alternative(admin_html, "text/html")
            admin_msg.send()

            # User confirmation email
            user_context = {
                "full_name": full_name,
                "subject": subject,
            }

            user_html = render_to_string(
                "emails/contact_confirmation.html",
                user_context
            )

            user_msg = EmailMultiAlternatives(
                subject="We received your message",
                body="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )

            user_msg.attach_alternative(user_html, "text/html")
            user_msg.send()

            messages.success(
                request,
                "Thank you for reaching out! We'll get back to you soon."
            )

            return redirect("home:contact")

        except Exception as e:

            messages.error(
                request,
                f"An error occurred. Please try again. Error: {str(e)}"
            )

            return render(request, "home/contact.html")

    return render(request, "home/contact.html")


def terms(request):
    return render(request, "home/legal/terms.html")


def privacy(request):
    return render(request, "home/legal/privacy.html")


def refund(request):
    return render(request, "home/legal/refund.html")


def shipping(request):
    return render(request, "home/legal/shipping.html")


def watch_demo(request):

    cache_key = "demo_video"

    demo = cache.get(cache_key)

    if not demo:
        demo = (
            DemoVideo.objects
            .filter(is_active=True)
            .order_by("-created_at")
            .first()
        )

        cache.set(cache_key, demo, 300)

    return render(
        request,
        "home/watch_demo.html",
        {
            "demo": demo
        }
    )


def search_webinars(request):

    query = request.GET.get("q", "").strip()

    if not query:
        return render(
            request,
            "home/search_results.html",
            {
                "query": "",
                "live_results": [],
                "recorded_results": [],
                "total_results": 0,
                "instructor_name": None,
            }
        )

    cache_key = f"search_{query.lower()}"

    cached_data = cache.get(cache_key)

    if cached_data:
        return render(
            request,
            "home/search_results.html",
            cached_data
        )

    cutoff_time = timezone.now() - timedelta(hours=48)

    live_results = list(
        LiveWebinar.objects.filter(
            Q(title__icontains=query) |
            Q(instructor__name__icontains=query) |
            Q(category__name__icontains=query),
            start_datetime__gte=cutoff_time
        )
        .select_related("instructor", "category")
        .only(
            "id",
            "title",
            "start_datetime",
            "instructor__name",
            "category__name",
        )[:10]
    )

    recorded_results = list(
        RecordedWebinar.objects.filter(
            Q(title__icontains=query) |
            Q(instructor__name__icontains=query) |
            Q(category__name__icontains=query)
        )
        .select_related("instructor", "category")
        .only(
            "id",
            "title",
            "instructor__name",
            "category__name",
        )[:10]
    )

    total_results = len(live_results) + len(recorded_results)

    context = {
        "query": query,
        "live_results": live_results,
        "recorded_results": recorded_results,
        "total_results": total_results,
        "instructor_name": None,
    }

    cache.set(cache_key, context, 120)

    return render(
        request,
        "home/search_results.html",
        context
    )


@require_POST
def newsletter_subscribe(request):

    email = request.POST.get("email", "").strip()

    if not email:
        return JsonResponse({
            "success": False,
            "message": "Email is required"
        })

    try:

        subscriber, created = (
            NewsletterSubscriber.objects
            .get_or_create(email=email)
        )

        if created:
            return JsonResponse({
                "success": True,
                "message": (
                    "Thank you for subscribing! "
                    "Stay updated with our latest webinars and offers."
                )
            })

        return JsonResponse({
            "success": False,
            "message": "This email is already subscribed"
        })

    except Exception:
        return JsonResponse({
            "success": False,
            "message": "An error occurred. Please try again."
        })


@require_POST
def dismiss_promo(request):

    if "show_subscription_promo" in request.session:
        del request.session["show_subscription_promo"]

    return JsonResponse({
        "success": True
    })