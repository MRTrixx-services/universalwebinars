from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from orders.models import Order

from django.core.cache import cache

@login_required
def enrollments_view(request):

    cache_key = f"user_enrollments_{request.user.id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return render(request, 'profile/enrollments.html', cached_data)

    paid_orders = (
        Order.objects
        .filter(user=request.user, status="PAID")
        .prefetch_related("items")
        .only("id", "total_amount", "created_at")
    )

    purchased_items = []
    total_spent = 0
    upcoming_count = 0
    recorded_count = 0
    categories = set()

    for order in paid_orders:
        total_spent += float(order.total_amount)

        for item in order.items.all():

            variant = item.variant.upper()

            if variant.startswith("LIVE"):
                webinar_type = "LIVE"
                upcoming_count += 1
            elif variant.startswith("REC"):
                webinar_type = "RECORDED"
                recorded_count += 1
            else:
                webinar_type = "UNKNOWN"

            if item.category_name:
                categories.add(item.category_name)

            purchased_items.append({
                "title": item.webinar_title,
                "variant": item.variant,
                "type": webinar_type,
                "price": item.price,
                "instructor": item.instructor_name or "N/A",
                "category": item.category_name or "N/A",
                "date": order.created_at.strftime("%b %d, %Y"),
                "join_link": None,
                "watch_link": None
            })

    total_enrollments = len(purchased_items)

    completion_rate = (
        "0%" if total_enrollments == 0
        else f"{min(100, int((recorded_count / total_enrollments) * 100))}%"
    )

    context = {
        'active_tab': 'enrollments',
        'purchased_items': purchased_items,

        'total_enrollments': total_enrollments,
        'completion_rate': completion_rate,
        'total_spent': f"{total_spent:.2f}",

        'upcoming_count': upcoming_count,
        'recordings_count': recorded_count,
        'recorded_count': recorded_count,

        'completed_count': 0,
        'missed_count': 0,

        'categories': sorted(categories)
    }

    # 🔥 CACHE SAVE (IMPORTANT)
    cache.set(cache_key, context, 120)

    return render(request, 'profile/enrollments.html', context)


@login_required
def subscriptions_view(request):
    from subscriptions.models import UserSubscription, SubscriptionPlan, SubscriptionPayment
    from django.utils import timezone
    from datetime import timedelta
    
    # Get active subscription
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        status='ACTIVE',
        end_date__gte=timezone.now()
    ).select_related('plan').first()
    
    # Calculate progress if active subscription exists
    days_remaining = None
    progress_percent = 0
    if active_subscription:
        total_days = (active_subscription.end_date - active_subscription.start_date).days
        elapsed_days = (timezone.now() - active_subscription.start_date).days
        days_remaining = (active_subscription.end_date - timezone.now()).days
        progress_percent = min(100, int((elapsed_days / total_days) * 100)) if total_days > 0 else 0
    
    # Get available plans
    available_plans = SubscriptionPlan.objects.filter(is_active=True).order_by('duration_months')
    
    # Get payment history
    payments = SubscriptionPayment.objects.filter(user=request.user).select_related('plan').order_by('-created_at')
    payment_count = payments.filter(status='PAID').count()
    
    return render(request, 'profile/subscriptions.html', {
        'active_tab': 'subscriptions',
        'active_subscription': active_subscription,
        'days_remaining': days_remaining,
        'progress_percent': progress_percent,
        'available_plans': available_plans,
        'payments': payments,
        'payment_count': payment_count
    })

# @login_required
# def orders_view(request):
#     user_orders = Order.objects.filter(user=request.user).prefetch_related('items__webinar').order_by('-created_at')
    
#     orders_data = []
#     for order in user_orders:
#         items_list = []
#         for item in order.items.all():
#             webinar = item.webinar
#             instructor_name = None
#             if webinar and hasattr(webinar, 'instructor'):
#                 instructor_name = webinar.instructor.name if hasattr(webinar.instructor, 'name') else str(webinar.instructor)
            
#             items_list.append({
#                 'title': webinar.title if webinar else 'N/A',
#                 'variant': item.variant,
#                 'price': item.price,
#                 'image': getattr(webinar, 'poster', None).url if hasattr(webinar, 'poster') and webinar.poster else None,
#                 'instructor': instructor_name
#             })
        
#         orders_data.append({
#             'order_number': order.order_number,
#             'status': order.status.lower(),
#             'total': order.total_amount,
#             'placed_at': order.created_at.strftime('%b %d, %Y at %I:%M %p'),
#             'completed_at': order.created_at.strftime('%b %d, %Y') if order.status == 'PAID' else None,
#             'payment_method': 'PayPal' if order.payment_id else 'N/A',
#             'items': items_list
#         })
    
#     completed_count = user_orders.filter(status='PAID').count()
    
#     return render(request, 'profile/orders.html', {
#         'active_tab': 'orders',
#         'orders': orders_data,
#         'completed_count': completed_count
#     })

@login_required
def orders_view(request):
    orders = Order.objects.filter(
        user=request.user,
        status="PAID"
    ).prefetch_related("items").order_by("-created_at")

    return render(request, "profile/orders.html", {
        "active_tab": "orders",
        "orders": orders,
        "completed_count": orders.count()
    })

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile:edit')
    return render(request, 'profile/edit.html', {'active_tab': 'edit'})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile:change_password')
    return render(request, 'profile/change_password.html', {'active_tab': 'password'})
