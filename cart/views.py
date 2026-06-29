import json
from django.shortcuts import redirect
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

        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        total_mrp = sum((item.product.mrp * item.quantity) for item in cart_items if hasattr(item.product, 'mrp'))
        subtotal = sum(item.total_price for item in cart_items)
        listing_discount = total_mrp - subtotal

        shipping = 100 if subtotal > 0 else 0
        grand_total = subtotal + shipping
        
        coupon_id = self.request.session.get("coupon_id")
        coupon_code = ""
        discount = 0

        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            
            if coupon and coupon.is_valid():
                coupon_code = coupon.code
                
                if coupon.discount_type == 'percent':
                    discount = float(grand_total) * (float(coupon.discount) / 100.0)
                    if discount > grand_total:
                        discount = grand_total
                else:
                    discount = float(coupon.discount)
                
                self.request.session["discount"] = round(discount, 2)
            else:
                self.request.session.pop("coupon_id", None)
                self.request.session.pop("discount", None)
                discount = 0
                coupon_code = ""

        final_total = grand_total - discount
        if final_total < 0:
            final_total = 0
            
        has_items = cart_items.exists()
        has_out_of_stock = CartItem.objects.filter(
            cart=cart,
            product__stock__lte=0
        ).exists()

        context["total_mrp"] = total_mrp
        context["listing_discount"] = listing_discount
        context["discount"] = round(discount, 2)
        context["coupon_code"] = coupon_code
        context["final_total"] = round(final_total, 2)
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

            quantity = int(data.get("quantity", 1))

            color = data.get("color", "")

            size = data.get("size", "")

        except:

            quantity = 1
            color = ""
            size = ""
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
            product=product,
            color=color,
            size=size
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

            quantity=quantity,
            color=color,
            size=size

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

class ApplyCouponView(LoginRequiredMixin, View):

    def post(self, request):
        code = request.POST.get("coupon")
        
        if not code:
            try:
                data = json.loads(request.body)
                code = data.get("coupon") or data.get("code")
            except Exception:
                code = None

        if not code:
            return JsonResponse({
                "success": False,
                "message": "Please enter a valid coupon code."
            })

        try:
            coupon = Coupon.objects.get(code__iexact=code.strip())

        except Coupon.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Invalid coupon code"
            })

        if not coupon.is_valid():
            return JsonResponse({
                "success": False,
                "message": "This coupon is either inactive or has expired."
            })

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        subtotal = sum(item.total_price for item in cart_items)
        
        if subtotal < coupon.minimum_amount:
            return JsonResponse({
                "success": False,
                "message": f"This coupon requires a minimum purchase of ₹{coupon.minimum_amount}. Your current subtotal is ₹{subtotal}."
            })

        shipping = 100 if subtotal > 0 else 0
        grand_total = subtotal + shipping

        discount = 0
        if coupon.discount_type == 'percent':
            discount = float(grand_total) * (float(coupon.discount) / 100.0)
            if discount > grand_total:
                discount = grand_total
        else:
            discount = float(coupon.discount)

        final_total = float(grand_total) - discount
        if final_total < 0:
            final_total = 0

        request.session["coupon_id"] = coupon.id
        request.session["discount"] = round(discount, 2)

        return JsonResponse({
            "success": True,
            "coupon_code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount": round(discount, 2),
            "final_total": round(final_total, 2),
            "message": "Coupon applied successfully"
        })
        
class RemoveCouponView(LoginRequiredMixin, View):
    def post(self, request):
        request.session.pop("coupon_id", None)
        request.session.pop("discount", None)
        return redirect("checkout")