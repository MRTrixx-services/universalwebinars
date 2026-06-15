from django.db import models
from live_webinars.models import LiveWebinar


class ZoomMeeting(models.Model):

    webinar = models.OneToOneField(
        LiveWebinar,
        on_delete=models.CASCADE,
        related_name="zoom_meeting"
    )

    zoom_meeting_id = models.CharField(max_length=50)
    uuid = models.CharField(max_length=255, blank=True, null=True)

    topic = models.CharField(max_length=500)

    join_url = models.URLField(max_length=500)
    start_url = models.URLField(blank=True, null=True,max_length=500)

    password = models.CharField(max_length=20, blank=True, null=True)

    start_time = models.DateTimeField()
    duration = models.PositiveIntegerField()

    timezone = models.CharField(max_length=50, default="UTC")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic} ({self.zoom_meeting_id})"