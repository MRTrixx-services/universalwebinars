from django.urls import path
from .views import (
    subscription_list,
    create_subscription_payment,
    capture_subscription_payment,activate_subscription
)

app_name = "subscriptions"

urlpatterns = [
    path("", subscription_list, name="list"),

    path("paypal/create/<int:plan_id>/", create_subscription_payment, name="paypal_create"),

    path("paypal/capture/<int:plan_id>/<str:paypal_id>/", capture_subscription_payment, name="paypal_capture"),
    path("activate/", activate_subscription, name="activate"),
    path("plans/", subscription_list, name="plans"),

]