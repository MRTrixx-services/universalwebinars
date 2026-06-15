from django.db import models
from django.utils import timezone
from django.db.models import Max
from live_webinars.models import Instructor, WebinarCategory
from ckeditor.fields import RichTextField


class RecordedWebinar(models.Model):
    webinar_id = models.CharField(
        max_length=15,
        unique=True,
        editable=False
    )

    category = models.ForeignKey(
        WebinarCategory,
        on_delete=models.PROTECT,
        related_name="recorded_webinars"
    )

    title = models.CharField(max_length=255)

    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name="recorded_webinars"
    )

    duration_minutes = models.PositiveIntegerField()
    description = RichTextField(blank=True, null=True)
    zoom_recording_link = models.URLField(
        blank=True,
        null=True,
        help_text="Private link (paid users only)"
    )

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.webinar_id:
            now = timezone.now()
            prefix = f"REC{now.strftime('%y%m')}"

            last_id = (
                RecordedWebinar.objects
                .filter(webinar_id__startswith=prefix)
                .aggregate(Max("webinar_id"))["webinar_id__max"]
            )

            if last_id:
                last_number = int(last_id[-3:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.webinar_id = f"{prefix}{str(new_number).zfill(3)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class RecordedWebinarPricing(models.Model):
    webinar = models.OneToOneField(
        RecordedWebinar,
        related_name="pricing",
        on_delete=models.CASCADE
    )

    single_price = models.DecimalField(max_digits=8, decimal_places=2)
    multi_user_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Pricing - {self.webinar.title}"


