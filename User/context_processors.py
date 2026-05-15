from .models import Wishlist, CartItem


def global_counts(request):

    wishlist_count = 0
    cart_count = 0

    if request.user.is_authenticated:

        # Wishlist Count
        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

        # Cart Count
        cart_count = CartItem.objects.filter(
            cart__user=request.user
        ).count()

    return {

        'wishlist_count': wishlist_count,
        'cart_count': cart_count,

    }