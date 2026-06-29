from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from User.models import *
import json
from django.views import View


class WishlistAPIView(LoginRequiredMixin, View):

    def post(self, request):

        # ✅ FIX: JSON support
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
        except:
            product_id = request.POST.get("product_id")

        if not product_id:
            return JsonResponse({
                "status": "error",
                "message": "Product id required"
            }, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Product not found"
            }, status=404)

        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).first()

        if wishlist_item:
            wishlist_item.delete()
            status_msg = "removed"
        else:
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            status_msg = "added"

        wishlist_count = Wishlist.objects.filter(user=request.user).count()

        return JsonResponse({
            "status": status_msg,
            "wishlist_count": wishlist_count
        })


class WishlistDataAPIView(LoginRequiredMixin, View):

    def get(self, request):

        cache_key = f"wishlist_{request.user.id}"

        cached_data = cache.get(cache_key)

        # RETURN CACHE DATA
        if cached_data:
            return JsonResponse({
                "cached": True,
                "wishlist": cached_data
            })

        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related("product")

        data = []

        for item in wishlist_items:

            data.append({
                "id": item.product.id,
                "name": item.product.name,
                "slug": item.product.slug,
                "price": str(item.product.price),
            })

        cache.set(cache_key, data, timeout=300)

        return JsonResponse({
            "cached": False,
            "wishlist": data
        })


class WishlistPageView(TemplateView):

    template_name = "wishlist.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            wishlist_items = Wishlist.objects.filter(
                user=self.request.user
            ).select_related(
                "product"
            ).prefetch_related(
                "product__images"
            )

            wishlist_data = []

            for item in wishlist_items:

                product = item.product

                # =========================
                # CHECK CART
                # =========================

                in_cart = CartItem.objects.filter(
                    cart__user=self.request.user,
                    product=product
                ).exists()
                
                reviews = Review.objects.filter(
                    order__items__product=product
                )

                avg_rating = reviews.aggregate(
                    Avg("rating")
                )["rating__avg"] or 0

                avg_rating = round(avg_rating, 1)

                total_reviews = reviews.count()

                wishlist_data.append({

                    "id": product.id,

                    "name": product.name,
                    
                    "slug": product.slug,
                    
                    "mrp": product.mrp,
                    
                    "final_price": product.final_price(),

                    "discount": product.discount,

                    "discount_percent":
                    product.discount_percent(),

                    "image":
                    product.images.first().image.url
                    if product.images.first()
                    else "",

                    "in_cart": in_cart,
                    "colors": product.colors.all(),
                    "sizes": product.sizes.all(),
                    "images": product.images.all(),
                    
                    "avg_rating": avg_rating,
                    "total_reviews": total_reviews,

                })

            context["wishlist_items"] = wishlist_data

            context["wishlist_count"] = len(
                wishlist_data
            )

        else:

            context["wishlist_items"] = []

            context["wishlist_count"] = 0

        return context