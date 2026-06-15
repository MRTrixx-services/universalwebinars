from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import ZoomService

from django.http import JsonResponse


@api_view(["GET"])
def list_zoom_meetings(request):

    zoom = ZoomService()

    meetings = zoom.list_meetings()

    return Response(meetings)


@api_view(["GET"])
def search_zoom_meetings(request):

    query = request.GET.get("q")

    zoom = ZoomService()

    meetings = zoom.search_meetings(query)

    return Response({
        "results": meetings
    })

def test_zoom_meetings(request):

    zoom = ZoomService()

    meetings = zoom.list_meetings()

    return JsonResponse({"meetings": meetings})

@api_view(["GET"])
def search_zoom_recordings(request):

    query = request.GET.get("q")

    zoom = ZoomService()

    recordings = zoom.search_recordings(query)

    return Response({
        "results": recordings
    })

@api_view(["GET"])
def debug_zoom_recordings(request):

    zoom = ZoomService()

    recordings = zoom.list_recordings()

    return Response(recordings)