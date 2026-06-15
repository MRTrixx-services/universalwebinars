from django.urls import path
from .views import (
    enrollments_view,
    subscriptions_view,
    orders_view,
    edit_profile_view,
    change_password_view
)

app_name = 'profile'

urlpatterns = [
    path('enrollments/', enrollments_view, name='enrollments'),
    path('subscriptions/', subscriptions_view, name='subscriptions'),
    path('orders/', orders_view, name='orders'),
    path('edit/', edit_profile_view, name='edit'),
    path('change-password/', change_password_view, name='change_password'),
]
