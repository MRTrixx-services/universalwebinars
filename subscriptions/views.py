from django.shortcuts import render
from .models import SubscriptionPlan
from django.conf import settings

from django.http import JsonResponse
from .models import SubscriptionPlan, UserSubscription,SubscriptionPayment
from orders.paypal import get_access_token
import requests

from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.contrib.auth.decorators import login_required

import json
from django.views.decorators.csrf import csrf_exempt

from .email_utils import send_subscription_email


def subscription_list(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    selected_plan_id = request.GET.get('plan', None)

    return render(request, "subscriptions/list.html", {
        "plans": plans,
        "PAYPAL_CLIENT_ID": settings.PAYPAL_CLIENT_ID,
        "selected_plan_id": selected_plan_id
    })

@login_required
def create_subscription_payment(request, plan_id):

    plan = SubscriptionPlan.objects.get(id=plan_id)

    # create pending payment record first
    payment = SubscriptionPayment.objects.create(
        user=request.user,
        plan=plan
    )

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
                "value": str(plan.price)
            }
        }]
    }

    res = requests.post(url, json=data, headers=headers)
    response = res.json()

    if "id" not in response:
        payment.status = "FAILED"
        payment.save()
        return JsonResponse(response, status=400)

    payment.paypal_id = response["id"]
    payment.save()

  

    return JsonResponse({
        "id": response["id"],
        "payment_db_id": payment.id
    })

@login_required
def capture_subscription_payment(request, plan_id, paypal_id):

    payment = SubscriptionPayment.objects.get(
        paypal_id=paypal_id,
        user=request.user
    )

    plan = payment.plan

    access_token = get_access_token()

    url = f"{settings.PAYPAL_BASE}/v2/checkout/orders/{paypal_id}/capture"

    headers = {
        "Content-Type":"application/json",
        "Authorization":f"Bearer {access_token}",
    }

    res = requests.post(url, headers=headers)

    if res.status_code == 201:

        payment.status = "PAID"
        payment.save()

        existing = UserSubscription.objects.filter(
            user=request.user,
            status="ACTIVE",
            end_date__gt=timezone.now()
        ).first()

        if existing:
            existing.end_date += relativedelta(months=plan.duration_months)
            existing.payment_id = paypal_id
            existing.save()

            subscription = existing

        else:
            start = timezone.now()
            end = start + relativedelta(months=plan.duration_months)

            subscription = UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                start_date=start,
                end_date=end,
                payment_id=paypal_id
            )

        try:
            send_subscription_email(subscription)
        except Exception as e:
            print("Subscription email failed:", e)

        return JsonResponse({"success":True})

    payment.status = "FAILED"
    payment.save()

    return JsonResponse({"success":False})


@login_required
def activate_subscription(request):

    data = json.loads(request.body)

    subscription_id = data["subscription_id"]
    plan_id = data["plan_id"]

    plan = SubscriptionPlan.objects.get(id=plan_id)

    existing = UserSubscription.objects.filter(
        user=request.user,
        status="ACTIVE",
        end_date__gt=timezone.now()
    ).first()

    if existing:
        existing.end_date += relativedelta(months=plan.duration_months)
        existing.payment_id = subscription_id
        existing.save()

        subscription = existing

    else:
        start = timezone.now()
        end = start + relativedelta(months=plan.duration_months)

        subscription = UserSubscription.objects.create(
        user=request.user,
        plan=plan,
        start_date=start,
        end_date=end,
        payment_id=subscription_id
    )

    try:
        send_subscription_email(subscription)
    except Exception as e:
        print("Subscription email failed:", e)

    return JsonResponse({"success":True})