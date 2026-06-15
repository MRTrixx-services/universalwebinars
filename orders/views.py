from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
from django.conf import settings
from .models import Order
from django.http import JsonResponse
from .paypal import get_access_token
import requests
from subscriptions.utils import has_active_subscription
from live_webinars.models import LiveWebinar
from .models import PaymentLog
from django.http import FileResponse
from .utils import generate_invoice_pdf
from .models import OrderItem
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, get_object_or_404
from django.shortcuts import get_object_or_404
from .email_utils import send_invoice_email

@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("cart:cart_page")

    subscribed = has_active_subscription(request.user)

    total = 0
    for item in cart_items:
        price = item.price_snapshot
        if subscribed and item.variant in ["LIVE_SINGLE", "LIVE_MULTI"]:
            price = 0
        total += price

    # Always create fresh PENDING order
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        status="PENDING"
    )

    from .models import OrderItem

    # ✅ OrderItems here itself snapshot pannidu
    for item in cart_items:
        price = item.price_snapshot
        if subscribed and item.variant in ["LIVE_SINGLE", "LIVE_MULTI"]:
            price = 0

        webinar = item.webinar

        instructor_name = None
        category_name = None

        if webinar:
            # 🔥 instructor
            if hasattr(webinar, "instructor") and webinar.instructor:
                instructor_name = webinar.instructor.name

            # 🔥 category
            if hasattr(webinar, "category") and webinar.category:
                category_name = webinar.category.name
        OrderItem.objects.create(
            order=order,
            webinar_title=webinar.title if webinar else "Unknown Webinar",
            webinar_ref_id=str(item.object_id),
            variant=item.variant,
            price=price,
            instructor_name=instructor_name,
            category_name=category_name,
        )

    return render(request, "cart/checkout.html", {
        "items": cart_items,
        "total": total,
        "order": order,
        "PAYPAL_CLIENT_ID": settings.PAYPAL_CLIENT_ID
    })


@csrf_exempt
@login_required
def create_paypal_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Always create fresh PayPal order
    order.payment_id = None
    order.gateway_order_id = None
    order.save()

    access_token = get_access_token()

    url = f"{settings.PAYPAL_BASE}/v2/checkout/orders"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": str(order.total_amount)
            }
        }]
    }

    res = requests.post(url, json=data, headers=headers)

    try:
        response_json = res.json()
    except Exception:
        return JsonResponse({"error": "Invalid PayPal response"}, status=400)

    # ❗ ADD THIS
    if res.status_code != 201 or "id" not in response_json:
        return JsonResponse({
            "error": "Failed to create PayPal order",
            "details": response_json
        }, status=400)

    PaymentLog.objects.create(
        order=order,
        event="PAYPAL_CREATE_ORDER",
        request_data=data,
        response_data=response_json,
        status="SUCCESS" if res.status_code == 201 else "FAILED"
    )

    paypal_id = response_json["id"]

    order.payment_id = paypal_id
    order.gateway_order_id = paypal_id
    order.save()

    return JsonResponse({"id": paypal_id})



@csrf_exempt
@login_required
def capture_paypal_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "PAID":
        return JsonResponse({"success": True})

    if not order.payment_id:
        return JsonResponse({"success": False, "error": "Missing PayPal order ID"})

    access_token = get_access_token()
    url = f"{settings.PAYPAL_BASE}/v2/checkout/orders/{order.payment_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    res = requests.post(url, headers=headers)

    try:
        response_data = res.json()
        PaymentLog.objects.create(
            order=order,
            event="PAYPAL_CAPTURE_PAYMENT",
            request_data={"order_id": order.payment_id},
            response_data=response_data,
            status="SUCCESS" if res.status_code == 201 else "FAILED"
        )
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid PayPal response"})

    if res.status_code == 201 and response_data.get("status") == "COMPLETED":

        try:
            capture = response_data["purchase_units"][0]["payments"]["captures"][0]
            capture_id = capture["id"]
            capture_status = capture["status"]
            paid_amount = float(capture["amount"]["value"])

            if capture_status != "COMPLETED":
                return JsonResponse({"success": False, "error": "Payment not completed"})

            if abs(paid_amount - float(order.total_amount)) > 0.01:
                return JsonResponse({"success": False, "error": "Payment amount mismatch"})

        except (KeyError, IndexError):
            return JsonResponse({"success": False, "error": "Invalid PayPal response"})

        # ✅ Just update status — items already created in checkout_view
        order.gateway_transaction_id = capture_id
        order.status = "PAID"
        order.save()

        # ✅ Delete cart after payment
        CartItem.objects.filter(user=request.user).delete()

        try:
            send_invoice_email(order)
        except Exception as e:
            print("Email failed:", e)

        return JsonResponse({
            "success": True,
            "transaction_id": order.payment_id,
            "gateway_order_id": order.gateway_order_id,
            "gateway_transaction_id": order.gateway_transaction_id,
            "items": [
                {"variant": i.variant, "price": str(i.price)}
                for i in order.items.all()
            ],
            "total": str(order.total_amount),
        })

    order.status = "FAILED"
    order.save()

    return JsonResponse({"success": False})



@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user,
        status="PAID"
    ).order_by("-created_at")

    return render(request, "profile/my_orders.html", {
        "orders": orders
    })

@login_required
def download_invoice(request, order_number):

    # admin can access any invoice
    if request.user.is_staff:
        order = get_object_or_404(
            Order,
            order_number=order_number,
            status="PAID"
        )
    else:
        # normal user → only own invoice
        order = get_object_or_404(
            Order,
            order_number=order_number,
            user=request.user,
            status="PAID"
        )

    pdf = generate_invoice_pdf(order)

    filename = order.invoice_number or order.order_number

    return FileResponse(
        pdf,
        as_attachment=True,
        filename=f"Workforce_{filename}.pdf"
    )

@login_required
def order_detail(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related("items__content_type"),
        order_number=order_number,
        user=request.user
    )

    return render(
        request,
        "invoice/order_detail.html",
        {
            "order": order
        }
    )
@csrf_exempt
@login_required
def create_order_before_payment(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return JsonResponse({"error": "Cart empty"}, status=400)

    subscribed = has_active_subscription(request.user)

    # ✅ Calculate total
    total = 0
    for item in cart_items:
        price = item.price_snapshot

        if subscribed and item.variant in ["LIVE_SINGLE", "LIVE_MULTI"]:
            price = 0

        total += price

    # ✅ Create new order (always fresh)
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        status="PENDING"
    )

    from .models import OrderItem

    # ✅ Create OrderItems (SNAPSHOT)
    for item in cart_items:

        price = item.price_snapshot

        if subscribed and item.variant in ["LIVE_SINGLE", "LIVE_MULTI"]:
            price = 0

        webinar = item.webinar

        OrderItem.objects.create(
            order=order,
            webinar_title=webinar.title if webinar else "Unknown Webinar",
            webinar_ref_id=str(item.object_id),
            variant=item.variant,
            price=price
        )

    return JsonResponse({
        "order_id": order.id,
        "message": "Order created successfully"
    })