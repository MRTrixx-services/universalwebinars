from .models import CartItem


def merge_cart_after_login(request, user, old_session_key):

    if not old_session_key:
        return

    guest_items = CartItem.objects.filter(session_key=old_session_key)

    for item in guest_items:

        exists = CartItem.objects.filter(
            user=user,
            content_type=item.content_type,
            object_id=item.object_id,
            variant=item.variant
        ).exists()

        if exists:
            item.delete()
        else:
            item.user = user
            item.session_key = None
            item.save()


def get_cart_owner(request):

    if request.user.is_authenticated:
        return {"user": request.user}

    if not request.session.session_key:
        request.session.create()

    return {"session_key": request.session.session_key}