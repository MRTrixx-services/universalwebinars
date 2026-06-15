from django.shortcuts import render, get_object_or_404
from .models import RecordedWebinar
from django.core.paginator import Paginator
from live_webinars.models import WebinarCategory, Instructor
from django.db.models import Q, Count

from django.core.cache import cache


def recorded_webinar_list(request):

    per_page = request.GET.get("per_page", 12)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 12

    # Base queryset
    queryset = (
        RecordedWebinar.objects
        .select_related("instructor", "category", "pricing")
        .filter(is_published=True)
        .order_by("-created_at")
    )

    # -----------------------
    # 🔍 Search
    # -----------------------
    search_query = request.GET.get("search")
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(instructor__name__icontains=search_query)
        )

    # -----------------------
    # 📂 Category Filter
    # -----------------------
    category_ids = request.GET.getlist("category")
    if category_ids:
        queryset = queryset.filter(category_id__in=category_ids)

    # -----------------------
    # 👨🏫 Instructor Filter
    # -----------------------
    instructor_ids = request.GET.getlist("instructor")
    if instructor_ids:
        queryset = queryset.filter(instructor_id__in=instructor_ids)

    # -----------------------
    # 📅 Month Filter
    # -----------------------
    month = request.GET.get("month")
    if month:
        try:
            queryset = queryset.filter(created_at__month=int(month))
        except ValueError:
            pass

    available_months = queryset.dates("created_at", "month")

    # 🔥 Detect active filters
    filters_active = any([
        search_query,
        category_ids,
        instructor_ids,
        month,
    ])

    # Pagination
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "webinars": page_obj.object_list,
        "page_obj": page_obj,
        "per_page": per_page,
        "categories": WebinarCategory.objects.annotate(webinar_count=Count("recorded_webinars", filter=Q(recorded_webinars__is_published=True))),
        "instructors": Instructor.objects.annotate(webinar_count=Count("recorded_webinars", filter=Q(recorded_webinars__is_published=True))),
        "selected_categories": category_ids,
        "selected_instructors": instructor_ids,
        "selected_month": month,
        "search_query": search_query,
        "available_months": available_months,
        "filters_active": filters_active,
    }

    return render(
        request,
        "recorded_webinars/recorded_list.html",
        context
    )


def recorded_webinar_detail(request, webinar_id):

    cache_key = f"recorded_detail_{webinar_id}"

    webinar = cache.get(cache_key)

    if not webinar:
        webinar = get_object_or_404(
            RecordedWebinar.objects.select_related(
                "category",
                "instructor",
                "pricing",
            ),
            webinar_id=webinar_id,
            is_published=True
        )

        cache.set(cache_key, webinar, 300)

    return render(
        request,
        "recorded_webinars/recorded_detail.html",
        {"webinar": webinar}
    )

