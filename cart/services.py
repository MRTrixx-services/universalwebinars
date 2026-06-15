# cart/services.py

from django.contrib.contenttypes.models import ContentType
from live_webinars.models import LiveWebinar
from recorded_webinars.models import RecordedWebinar
from .models import CartItem


def resolve_price(webinar, variant):

    # LIVE webinar pricing (6 variants)
    if hasattr(webinar, "pricing") and hasattr(webinar.pricing, "live_single_price"):
        p = webinar.pricing

        mapping = {
            "LIVE_SINGLE": p.live_single_price,
            "LIVE_MULTI": p.live_multi_price,
            "REC_SINGLE": p.recorded_single_price,
            "REC_MULTI": p.recorded_multi_price,
            "COMBO_SINGLE": p.combo_single_price,
            "COMBO_MULTI": p.combo_multi_price,
        }

        return mapping.get(variant)

    # RECORDED webinar pricing (2 variants)
    if hasattr(webinar, "pricing"):
        p = webinar.pricing

        mapping = {
            "REC_SINGLE": p.single_price,
            "REC_MULTI": p.multi_user_price,
        }

        return mapping.get(variant)

    return None


def get_owner(request):
    if request.user.is_authenticated:
        return {"user": request.user}

    if not request.session.session_key:
        request.session.create()

    return {"session_key": request.session.session_key}


def add_item_to_cart(request, webinar_type, webinar_id, variant):

    # fetch webinar
    if webinar_type == "live":
        webinar = LiveWebinar.objects.get(id=webinar_id)
    else:
        webinar = RecordedWebinar.objects.get(id=webinar_id)

    price = resolve_price(webinar, variant)

    content_type = ContentType.objects.get_for_model(webinar)

    owner = get_owner(request)

    CartItem.objects.get_or_create(
        content_type=content_type,
        object_id=webinar.id,
        variant=variant,
        defaults={"price_snapshot": price, **owner},
        **owner
    )