from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class CartItem(models.Model):

    VARIANT_CHOICES = [
        ("LIVE_SINGLE", "Live Single"),
        ("LIVE_MULTI", "Live Multi"),
        ("REC_SINGLE", "Recorded Single"),
        ("REC_MULTI", "Recorded Multi"),
        ("COMBO_SINGLE", "Combo Single"),
        ("COMBO_MULTI", "Combo Multi"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items"
    )

    session_key = models.CharField(max_length=40, null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    webinar = GenericForeignKey("content_type", "object_id")

    variant = models.CharField(max_length=20, choices=VARIANT_CHOICES)

    price_snapshot = models.DecimalField(max_digits=8, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "session_key", "content_type", "object_id", "variant")