from django.urls import path
from .views import list_zoom_meetings, search_zoom_meetings,test_zoom_meetings,search_zoom_recordings,debug_zoom_recordings

urlpatterns = [
    path("zoom/meetings/", list_zoom_meetings),
    path("zoom/search-meetings/", search_zoom_meetings),
    path("test/", test_zoom_meetings),
    path("zoom/search-recordings/",search_zoom_recordings),
    path(
    "zoom/debug-recordings/",
    debug_zoom_recordings,
    name="debug_zoom_recordings"
),
]