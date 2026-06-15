# cart/urls.py

from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_page, name="cart_page"),
    path("add/<str:webinar_type>/<int:webinar_id>/<str:variant>/",views.add_to_cart,name="add_to_cart"),
    path("remove/<int:item_id>/", views.remove_item, name="remove_item"),
]