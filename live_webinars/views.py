from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

from .models import LiveWebinar, WebinarCategory, Instructor
from subscriptions.models import SubscriptionPlan
from subscriptions.utils import has_active_subscription
from rest_framework.decorators import api_view
from rest_framework.response import Response
from integrations.services import create_zoom_meeting_for_webinar


def live_webinar_list(request):
    now = timezone.now()

    per_page = request.GET.get("per_page", 12)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 12

    webinars = (
        LiveWebinar.objects
        .filter(start_datetime__gte=now - timedelta(hours=48))
        .select_related("category", "instructor")
        .only(
            "id", "title", "slug", "start_datetime", "is_test",
            "category__name", "instructor__name"
        )
        .order_by("-is_test", "start_datetime")
    )

    search_query = request.GET.get("search")
    if search_query:
        webinars = webinars.filter(
            Q(title__icontains=search_query) |
            Q(instructor__name__icontains=search_query)
        )

    category_ids = request.GET.getlist("category")
    if category_ids:
        webinars = webinars.filter(category_id__in=category_ids)

    instructor_ids = request.GET.getlist("instructor")
    if instructor_ids:
        webinars = webinars.filter(instructor_id__in=instructor_ids)

    month = request.GET.get("month")
    if month:
        try:
            webinars = webinars.filter(start_datetime__month=int(month))
        except ValueError:
            pass

    query_string = request.GET.urlencode()
    cache_key = f"live_webinars_ids:{query_string}"
    webinar_ids = cache.get(cache_key)

    if webinar_ids is None:
        webinar_ids = list(webinars.values_list("id", flat=True))
        cache.set(cache_key, webinar_ids, 120)

    webinars = (
        LiveWebinar.objects
        .filter(id__in=webinar_ids)
        .select_related("category", "instructor")
        .only(
            "id", "title", "slug", "start_datetime", "is_test",
            "category__name", "instructor__name"
        )
        .order_by("-is_test", "start_datetime")
    )

    available_months = cache.get("live_months")
    if not available_months:
        available_months = list(
            LiveWebinar.objects.only("start_datetime")
            .dates("start_datetime", "month")
        )
        cache.set("live_months", available_months, 600)

    filters_active = any([search_query, category_ids, instructor_ids, month])

    paginator = Paginator(webinars, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    is_subscribed = False
    if request.user.is_authenticated:
        sub_key = f"user_sub:{request.user.id}"
        is_subscribed = cache.get(sub_key)
        if is_subscribed is None:
            is_subscribed = has_active_subscription(request.user)
            cache.set(sub_key, is_subscribed, 60)

    # Categories with webinar count
    categories = cache.get("categories_with_count")
    if not categories:
        categories = list(
            WebinarCategory.objects
            .annotate(webinar_count=Count('webinars'))
            .filter(webinar_count__gt=0)
            .only("id", "name")
            .order_by("name")
        )
        cache.set("categories_with_count", categories, 600)

    # Instructors with webinar count
    instructors = cache.get("instructors_with_count")
    if not instructors:
        instructors = list(
            Instructor.objects
            .annotate(webinar_count=Count('livewebinar'))
            .filter(webinar_count__gt=0)
            .only("id", "name")
            .order_by("name")
        )
        cache.set("instructors_with_count", instructors, 600)

    context = {
        "page_obj": page_obj,
        "webinars": page_obj.object_list,
        "per_page": per_page,
        "categories": categories,
        "instructors": instructors,
        "selected_categories": category_ids,
        "selected_instructors": instructor_ids,
        "selected_month": month,
        "search_query": search_query,
        "available_months": available_months,
        "filters_active": filters_active,
        "is_subscribed": is_subscribed,
    }

    return render(request, "live_webinars/list.html", context)


def live_webinar_detail(request, webinar_id, slug):

    cache_key = f"live_detail:{webinar_id}"
    webinar = cache.get(cache_key)

    if not webinar:
        webinar = get_object_or_404(
            LiveWebinar.objects.select_related("category", "instructor"),
            webinar_id=webinar_id,
        )
        cache.set(cache_key, webinar, 300)

    if webinar.slug != slug:
        return redirect(
            "live_webinars:detail",
            webinar_id=webinar.webinar_id,
            slug=webinar.slug
        )

    plans = cache.get("subscription_plans")
    if not plans:
        plans = list(
            SubscriptionPlan.objects
            .filter(is_active=True)
            .only("id", "name", "price")
        )
        cache.set("subscription_plans", plans, 600)

    is_subscribed = False
    if request.user.is_authenticated:
        sub_key = f"user_sub:{request.user.id}"
        is_subscribed = cache.get(sub_key)
        if is_subscribed is None:
            is_subscribed = has_active_subscription(request.user)
            cache.set(sub_key, is_subscribed, 60)

    return render(
        request,
        "live_webinars/detail.html",
        {
            "webinar": webinar,
            "subscription_plans": plans,
            "is_subscribed": is_subscribed,
        }
    )


@login_required
def join_live_webinar(request, webinar_id):

    webinar = get_object_or_404(LiveWebinar, webinar_id=webinar_id)

    if not has_active_subscription(request.user):
        return redirect("subscriptions:list")

    if webinar.dynamic_status != "LIVE":
        return redirect("live_webinars:detail", webinar_id=webinar_id)

    return redirect(webinar.zoom_meeting.join_url)
