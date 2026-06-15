from .models import CartItem

def cart_count(request):

    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        session_key = request.session.session_key
        if not session_key:
            count = 0
        else:
            count = CartItem.objects.filter(session_key=session_key).count()

    return {"cart_count": count}