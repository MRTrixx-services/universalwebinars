import uuid
from datetime import timedelta
from django.utils.timesince import timesince
from zoneinfo import ZoneInfo

from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

from django.utils.text import slugify


# -----------------------------
# GLOBAL PRICING
# -----------------------------
class GlobalPricing(models.Model):
    live_single_price = models.DecimalField(max_digits=8, decimal_places=2, default=149.00)
    live_multi_price = models.DecimalField(max_digits=8, decimal_places=2, default=399.00)
    recorded_single_price = models.DecimalField(max_digits=8, decimal_places=2, default=199.00)
    recorded_multi_price = models.DecimalField(max_digits=8, decimal_places=2, default=499.00)
    combo_single_price = models.DecimalField(max_digits=8, decimal_places=2, default=299.00)
    combo_multi_price = models.DecimalField(max_digits=8, decimal_places=2, default=699.00)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Pricing"
        verbose_name_plural = "Global Pricing"

    def __str__(self):
        return "Global Pricing Settings"

    @classmethod
    def get_pricing(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


# -----------------------------
# CATEGORY
# -----------------------------
class WebinarCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# -----------------------------
# INSTRUCTOR
# -----------------------------
class Instructor(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=150)
    organization = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)

    country = models.CharField(max_length=5, blank=True)

    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField()
    photo = models.ImageField(upload_to="webinars/instructors/")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} – {self.designation}"


# -----------------------------
# LIVE WEBINAR
# -----------------------------
class LiveWebinar(models.Model):
    WEBINAR_STATUS = (
        ("UPCOMING", "Upcoming"),
        ("LIVE", "Live"),
        ("ENDED", "Ended"),
    )

    webinar_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    category = models.ForeignKey(
        WebinarCategory,
        on_delete=models.PROTECT,
        related_name="webinars"
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=300,
        blank=True,
        help_text="Auto generated from title"
    )

    is_test = models.BooleanField(
        default=False,
        help_text="Mark this webinar as Test / Demo only"
    )

    

    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE
    )

    # zoom_link = models.URLField(
    #     blank=True,
    #     null=True,
    #     help_text="Private Zoom link (only for paid users)"
    # )

    start_datetime = models.DateTimeField()
    
    duration_minutes = models.PositiveIntegerField()
    description = RichTextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=WEBINAR_STATUS,
        default="UPCOMING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_datetime"]

    def __str__(self):
        return f"{self.title} ({self.webinar_id})"
    
    def get_absolute_url(self):
        return f"/webinars/{self.webinar_id}/{self.slug}/"

    # -----------------------------
    # AUTO ID + STATUS
    # -----------------------------
    

    def save(self, *args, **kwargs):

        if not self.webinar_id:
            self.webinar_id = self.generate_webinar_id()

        if not self.slug:
            self.slug = slugify(self.title)

        # Always treat admin input as Pacific Time
        pacific = ZoneInfo("America/Los_Angeles")

        if timezone.is_naive(self.start_datetime):
            self.start_datetime = timezone.make_aware(self.start_datetime, pacific)
        else:
            self.start_datetime = self.start_datetime.astimezone(pacific)

        # Store in UTC
        self.start_datetime = self.start_datetime.astimezone(ZoneInfo("UTC"))

        self.status = self.calculate_status()

        super().save(*args, **kwargs)

    @property
    def join_url(self):
        if hasattr(self, "zoom_meeting"):
            return self.zoom_meeting.join_url
        return None


    def generate_webinar_id(self):
        """
        Format: WEBYYMMNNN
        Example: WEB2512062
        """
        now = timezone.now()
        prefix = f"WEB{now.strftime('%y%m')}"

        last_webinar = (
            LiveWebinar.objects
            .filter(webinar_id__startswith=prefix)
            .order_by("-webinar_id")
            .first()
        )

        if last_webinar:
            last_number = int(last_webinar.webinar_id[-3:])
            next_number = last_number + 1
        else:
            next_number = 1

        return f"{prefix}{next_number:03d}"

    @property
    def end_datetime(self):
        return self.start_datetime + timedelta(minutes=self.duration_minutes)
    
    @property
    def est_time(self):
        """
        Return start time in EST
        """
        return self.start_datetime.astimezone(
            ZoneInfo("America/New_York")
        )

    @property
    def pst_time(self):
        """
        Return start time in PST
        """
        return self.start_datetime.astimezone(
            ZoneInfo("America/Los_Angeles")
        )


    def calculate_status(self):
        now = timezone.now()
        end_time = self.end_datetime

        if now < self.start_datetime:
            return "UPCOMING"
        elif self.start_datetime <= now <= end_time:
            return "LIVE"
        return "ENDED"
    
    @property
    def dynamic_status(self):
        now = timezone.now()

        if now < self.start_datetime:
            return "UPCOMING"

        if self.start_datetime <= now <= self.end_datetime:
            return "LIVE"

        return "ENDED"
    
    @property
    def starts_in(self):
        if self.dynamic_status == "UPCOMING":
            return timesince(self.start_datetime, timezone.now())
        return None

    @property
    def recently_ended(self):
        now = timezone.now()
        return self.end_datetime < now <= self.end_datetime + timedelta(hours=48)

    @property
    def pricing(self):
        """Return webinar pricing or global pricing"""
        try:
            return self.webinarpricing
        except:
            return GlobalPricing.get_pricing()



# -----------------------------
# PRICING (Optional Override)
# -----------------------------
class WebinarPricing(models.Model):
    webinar = models.OneToOneField(
        LiveWebinar,
        on_delete=models.CASCADE,
        related_name="webinarpricing"
    )

    # Live
    live_single_price = models.DecimalField(max_digits=8, decimal_places=2)
    live_multi_price = models.DecimalField(max_digits=8, decimal_places=2)

    # Recorded
    recorded_single_price = models.DecimalField(max_digits=8, decimal_places=2)
    recorded_multi_price = models.DecimalField(max_digits=8, decimal_places=2)

    # Combo
    combo_single_price = models.DecimalField(max_digits=8, decimal_places=2)
    combo_multi_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Custom Pricing for {self.webinar.webinar_id}"




