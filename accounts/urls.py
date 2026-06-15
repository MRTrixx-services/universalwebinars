from django.urls import path
from .views import (
    register_view, 
    login_view, 
    logout_view,
    forgot_password_view,
    verify_otp_view,
    resend_otp_view,
    reset_password_view
)

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("verify-otp/", verify_otp_view, name="verify_otp"),
    path("resend-otp/", resend_otp_view, name="resend_otp"),
    path("reset-password/", reset_password_view, name="reset_password"),
]
