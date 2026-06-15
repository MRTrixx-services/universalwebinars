from django.urls import path
from .views import live_webinar_list,live_webinar_detail,join_live_webinar


app_name = "live_webinars"

urlpatterns = [
    path("", live_webinar_list, name="list"),
    path("<str:webinar_id>/<slug:slug>/", live_webinar_detail, name="detail"),
    path("live-webinars/join/<str:webinar_id>/", join_live_webinar, name="join_live"),

]
