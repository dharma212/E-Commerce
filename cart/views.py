import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from User.models import *

class CartView(LoginRequiredMixin, TemplateView):

    template_name = "cart.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        cart, created = Cart.objects.get_or_create(
            user=self.request.user
        )

        cart_items = CartItem.objects.filter(
            cart=cart
        ).select_related(
            "product"
        )

        subtotal = sum(
            item.total_price for item in cart_items
        )

        shipping = 100 if subtotal > 0 else 0

        grand_total = subtotal + shipping
        has_items = cart_items.exists()
        has_out_of_stock = CartItem.objects.filter(
            cart=cart,
            product__stock__lte=0
        ).exists()

        context["cart_items"] = cart_items
        context["subtotal"] = subtotal
        context["shipping"] = shipping
        context["grand_total"] = grand_total
        context["has_items"] = has_items
        context["has_out_of_stock"] = has_out_of_stock

        return context


class AddToCartView(LoginRequiredMixin, View):

    def post(self, request, product_id):

        # =========================
        # PRODUCT
        # =========================

        product = get_object_or_404(
            Product,
            id=product_id
        )

        # =========================
        # CART
        # =========================

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        # =========================
        # JSON DATA
        # =========================

        try:

            data = json.loads(request.body)

            quantity = int(
                data.get("quantity", 1)
            )

        except:

            quantity = 1

        # =========================
        # STOCK LIMIT
        # =========================

        if quantity < 1:
            quantity = 1

        if quantity > product.stock:
            quantity = product.stock

        # =========================
        # CHECK CART ITEM
        # =========================

        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        # =========================
        # REMOVE
        # =========================

        if cart_item:

            cart_item.delete()

            cart_count = CartItem.objects.filter(
                cart=cart
            ).count()

            return JsonResponse({

                "status": "removed",

                "cart_count": cart_count

            })

        # =========================
        # ADD
        # =========================

        CartItem.objects.create(

            cart=cart,

            product=product,

            quantity=quantity

        )

        cart_count = CartItem.objects.filter(
            cart=cart
        ).count()

        return JsonResponse({

            "status": "added",

            "cart_count": cart_count,

            "quantity": quantity

        })


class UpdateCartView(View):

    def post(self, request, pk):

        try:

            cart_item = get_object_or_404(
                CartItem,
                id=pk,
                cart__user=request.user
            )

            body = request.body.decode("utf-8")

            data = json.loads(body)

            action = data.get("action")

            product_stock = int(cart_item.product.stock)

            # =====================
            # INCREASE
            # =====================
            if action == "increase":

                if cart_item.quantity < product_stock:

                    cart_item.quantity += 1

                    cart_item.save()

                    return JsonResponse({
                        "success": True
                    })

                else:

                    return JsonResponse({
                        "success": False,
                        "message": "Stock limit reached"
                    })

           # =====================
            # DECREASE
            # =====================
            elif action == "decrease":

                # minimum quantity 1
                if cart_item.quantity > 1:

                    cart_item.quantity -= 1

                    cart_item.save()

                    return JsonResponse({
                        "success": True
                    })

                else:

                    return JsonResponse({
                        "success": False,
                        "message": "Minimum quantity is 1"
                    })

        except Exception as e:

            print("ERROR =>", e)

            return JsonResponse({
                "success": False,
                "message": str(e)
            })


class RemoveCartView(LoginRequiredMixin, View):

    def post(self, request, cart_id):

        cart_item = get_object_or_404(

            CartItem,

            id=cart_id,

            cart__user=request.user

        )

        cart_item.delete()

        return JsonResponse({

            "success": True,
            "message": "Removed"

        })