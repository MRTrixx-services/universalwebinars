from django.urls import path
from . import views
from .views import create_paypal_order,capture_paypal_order

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("paypal/create/<int:order_id>/", create_paypal_order, name="paypal_create"),
    path("paypal/capture/<int:order_id>/", capture_paypal_order, name="paypal_capture"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("invoice/<str:order_number>/", views.download_invoice, name="download_invoice"),
    path("order/<str:order_number>/", views.order_detail, name="order_detail"),
    path("create-order/", views.create_order_before_payment, name="create_order"),
]
