from django.utils import timezone
from .models import UserSubscription

def has_active_subscription(user):

    sub = UserSubscription.objects.filter(
        user=user,
        status="ACTIVE"
    ).order_by("-end_date").first()

    if not sub:
        return False

    # auto expire check
    if sub.end_date < timezone.now():
        sub.status = "EXPIRED"
        sub.save()
        return False

    return True