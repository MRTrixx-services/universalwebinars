from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import RegisterForm
from cart.utils import merge_cart_after_login
from django.core.mail import send_mail
from django.conf import settings
import random
from django.contrib.auth import get_user_model

from core.mail import send_welcome_email

User = get_user_model()
# ----------------------------
# REGISTER VIEW
# ----------------------------
@require_http_methods(["GET", "POST"])
def register_view(request):

    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            user.set_password(form.cleaned_data["password"])
            user.is_active = True
            user.save()

# Try sending welcome email but don't crash if it fails
            try:
                send_welcome_email(user)
            except Exception as e:
                print("Welcome email error:", e)

            messages.success(
                request,
                "Account created successfully. Please login."
            )

            return redirect("accounts:login")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})

# ----------------------------
# LOGIN VIEW
# ----------------------------
@require_http_methods(["GET", "POST"])
def login_view(request):

    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            old_session = request.session.session_key

            login(request, user)
            request.session.cycle_key()

            # 🔥 merge guest cart → user cart
            merge_cart_after_login(request, user, old_session)

            # Session expiry logic
            if remember:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(86400)
            
            # Set flag to show subscription promo
            request.session['show_subscription_promo'] = True


            if user.is_staff or user.is_superuser:
                return redirect("adminpanel:dashboard")
            
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url:
                return redirect(next_url)

            return redirect("home:home")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html")


# ----------------------------
# LOGOUT VIEW
# ----------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


# ----------------------------
# FORGOT PASSWORD VIEWS
# ----------------------------
@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session["reset_otp"] = otp
            request.session["reset_email"] = email
            request.session.set_expiry(600)  # 10 min
            
            try:
                send_mail(
                    "Password Reset OTP - dailyrespond",
                    f"Your OTP for password reset is: {otp}\n\nValid for 10 minutes.",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print("Email error:", e)
                messages.error(request, "Email service temporarily unavailable.")
                return redirect("accounts:forgot_password")
            
            messages.success(request, "OTP sent to your email!")
            return redirect("accounts:verify_otp")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
    
    return render(request, "accounts/forgot_password.html")


@require_http_methods(["GET", "POST"])
def verify_otp_view(request):
    if "reset_email" not in request.session:
        return redirect("accounts:forgot_password")
    
    if request.method == "POST":
        otp_input = "".join([
            request.POST.get(f"otp{i}", "").strip() for i in range(1, 7)
        ])
        
        stored_otp = str(request.session.get("reset_otp", ""))
        
        # Debug - remove after testing
        print(f"Input OTP: '{otp_input}' (len={len(otp_input)})")
        print(f"Stored OTP: '{stored_otp}' (len={len(stored_otp)})")
        print(f"Match: {otp_input == stored_otp}")
        
        if otp_input == stored_otp:
            request.session["otp_verified"] = True
            return redirect("accounts:reset_password")
        else:
            messages.error(request, f"Invalid OTP. Please try again.")
    
    return render(request, "accounts/verify_otp.html")


@require_http_methods(["GET", "POST"])
def resend_otp_view(request):
    email = request.session.get("reset_email")
    
    if not email:
        return redirect("accounts:forgot_password")
    
    otp = str(random.randint(100000, 999999))
    request.session["reset_otp"] = otp
    request.session.set_expiry(600)
    
    send_mail(
        "Password Reset OTP - dailyrespond",
        f"Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.\n\nIf you didn't request this, please ignore this email.",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    
    messages.success(request, "New OTP sent to your email!")
    return redirect("accounts:verify_otp")


@require_http_methods(["GET", "POST"])
def reset_password_view(request):
    if not request.session.get("otp_verified"):
        return redirect("accounts:forgot_password")
    
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/reset_password.html")
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "accounts/reset_password.html")
        
        email = request.session.get("reset_email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        
        # Clear session
        del request.session["reset_otp"]
        del request.session["reset_email"]
        del request.session["otp_verified"]
        
        messages.success(request, "Password reset successful! Please login.")
        return redirect("accounts:login")
    
    return render(request, "accounts/reset_password.html")
