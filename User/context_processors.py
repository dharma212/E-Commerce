from .models import Wishlist, CartItem, Category

def global_counts(request):

    wishlist_count = 0
    cart_count = 0

    if request.user.is_authenticated:

        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

        cart_count = CartItem.objects.filter(
            cart__user=request.user
        ).count()

    categories = Category.objects.prefetch_related(
        'types'
    ).all()

    return {

        'wishlist_count': wishlist_count,

        'cart_count': cart_count,

        'categories': categories,
    }