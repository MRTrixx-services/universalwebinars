from django.urls import path
from . import views

app_name = "recorded_webinars"

urlpatterns = [
    path("", views.recorded_webinar_list, name="list"),
    path("<str:webinar_id>/", views.recorded_webinar_detail, name="detail"),
]
