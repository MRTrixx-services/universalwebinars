from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .services import add_item_to_cart
from .utils import get_cart_owner
from .models import CartItem
from subscriptions.utils import has_active_subscription

@require_POST  # ✅ POST மட்டும் accept pannuvom
def add_to_cart(request, webinar_type, webinar_id, variant):

    # 🔐 HARD SECURITY — block live purchase for subscribers
    if request.user.is_authenticated and has_active_subscription(request.user):
        if variant in ["LIVE_SINGLE", "LIVE_MULTI"]:
            return JsonResponse({"status": "skipped"})

    add_item_to_cart(request, webinar_type, webinar_id, variant)

    return JsonResponse({"status": "added"})  # ✅ JSON response — JS handle pannuvom


def cart_page(request):
    owner = get_cart_owner(request)
    items = CartItem.objects.filter(**owner)
    total = sum(i.price_snapshot for i in items)
    return render(request, "cart/cart.html", {
        "items": items,
        "total": total
    })


def remove_item(request, item_id):
    owner = get_cart_owner(request)
    item = get_object_or_404(CartItem, id=item_id, **owner)
    webinar_title = item.webinar.title
    item.delete()
    messages.success(request, f'"{webinar_title}" has been removed from your cart')
    return redirect("cart:cart_page")