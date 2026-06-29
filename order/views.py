from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from User.models import *
import secrets
from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import JsonResponse
from django.views import View

class checkoutview(LoginRequiredMixin, TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        buy_now_id = self.request.GET.get('buy_now')
        buy_now_qty = self.request.GET.get('qty')
        buy_now_color = self.request.GET.get('color')
        buy_now_size = self.request.GET.get('size')

        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            qty = int(buy_now_qty) if buy_now_qty else 1
            subtotal = product.final_price() * qty 
            total_mrp = product.mrp * qty
            
            context["cart_items"] = [{
                'product': product,
                'quantity': qty,
                'color': buy_now_color,
                'size': buy_now_size,
                'total_price': subtotal
            }]
            context["buy_now_id"] = buy_now_id
            context["buy_now_qty"] = qty
            context["buy_now_color"] = buy_now_color
            context["buy_now_size"] = buy_now_size
        else:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_items = CartItem.objects.filter(cart=cart).select_related("product")
            subtotal = sum(item.total_price for item in cart_items) if cart_items.exists() else 0
            total_mrp = sum(item.product.mrp * item.quantity for item in cart_items) if cart_items.exists() else 0
            context["cart_items"] = cart_items

        shipping = 100 if subtotal > 0 else 0
        grand_total = subtotal + shipping

        coupon_id = self.request.session.get("coupon_id")
        coupon_code = ""
        coupon_discount = 0

        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon and coupon.is_valid():
                coupon_code = coupon.code
                if coupon.discount_type == 'percent':
                    coupon_discount = float(grand_total) * (float(coupon.discount) / 100.0)
                    if coupon_discount > grand_total:
                        coupon_discount = grand_total
                else:
                    coupon_discount = float(coupon.discount)
            else:
                self.request.session.pop("coupon_id", None)
                self.request.session.pop("discount", None)

        final_total = float(grand_total) - float(coupon_discount)
        if final_total < 0:
            final_total = 0

        total_savings = (total_mrp - subtotal) + coupon_discount
        if total_savings < 0:
            total_savings = 0

        context["total_mrp"] = total_mrp
        context["total_savings"] = total_savings
        context["subtotal"] = subtotal
        context["shipping"] = shipping
        context["grand_total"] = final_total 
        context["coupon_code"] = coupon_code
        context["coupon_discount"] = coupon_discount
        
        default_addr = Address.objects.filter(user=user, is_default=True).first()
        if not default_addr:
            default_addr = Address.objects.filter(user=user).first()
            
        context["default_address"] = default_addr
        context["addresses"] = Address.objects.filter(user=user)
        context["profile"] = Profile.objects.filter(user=user).first()
        all_coupons = Coupon.objects.filter(
            valid_to__gte=timezone.now()
        )

        used_coupon_ids = UserCoupon.objects.filter(
            user=user,
            is_used=True
        ).values_list(
            "coupon_id",
            flat=True
        )

        context["available_coupons"] = all_coupons.exclude(
            id__in=used_coupon_ids
        )

        context["used_coupons"] = all_coupons.filter(
            id__in=used_coupon_ids
        )
        
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        buy_now_id = request.POST.get("buy_now_id")
        buy_now_qty = request.POST.get("buy_now_qty")
        buy_now_color = request.POST.get("buy_now_color")
        buy_now_size = request.POST.get("buy_now_size")
        payment_method = request.POST.get("payment")
        selected_address_id = request.POST.get("selected_address") 

        if selected_address_id:
            order_address = get_object_or_404(Address, id=selected_address_id, user=user)
        else:
            order_address = Address.objects.filter(user=user, is_default=True).first() or Address.objects.filter(user=user).first()

        if not order_address:
            messages.error(request, "Please add a delivery address first.")
            return redirect("add_address")

        coupon_id = request.session.get("coupon_id")
        coupon_discount = 0
        coupon_code = ""
        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon and coupon.is_valid():
                coupon_code = coupon.code

        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            qty = int(buy_now_qty)
            subtotal = product.final_price() * qty
            grand_total = subtotal + 100
            
            if coupon_id and coupon:
                if coupon.discount_type == 'percent':
                    coupon_discount = float(grand_total) * (float(coupon.discount) / 100.0)
                else:
                    coupon_discount = float(coupon.discount)

            final_price = float(grand_total) - coupon_discount
            if final_price < 0: final_price = 0

            order = Order.objects.create(
                user=user, 
                address=order_address, 
                total_price=final_price, 
                status="Pending",
                payment_method=payment_method,
                # coupon_code=coupon_code,
                # coupon_discount=coupon_discount
            )
            if coupon_id and coupon:

                UserCoupon.objects.update_or_create(

                    user=user,
                    coupon=coupon,

                    defaults={
                        "order": order,
                        "is_used": True
                    }

                )
            if product.stock < qty:
                messages.error(request, f"Only {product.stock} items available in stock.")
                return redirect("checkout")

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.final_price(),
                color=buy_now_color,
                size=buy_now_size
            )

            product.stock -= qty
            product.save()
        else:
            # --- CART ORDER ---
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            if not cart_items.exists():
                return redirect("cart")

            subtotal = sum(item.total_price for item in cart_items)
            grand_total = subtotal + 100
            
            if coupon_id and coupon:
                if coupon.discount_type == 'percent':
                    coupon_discount = float(grand_total) * (float(coupon.discount) / 100.0)
                else:
                    coupon_discount = float(coupon.discount)

            final_price = float(grand_total) - coupon_discount
            if final_price < 0: final_price = 0

            order = Order.objects.create(
                user=user, 
                address=order_address, 
                total_price=final_price, 
                status="Pending",
                payment_method=payment_method
                # coupon_code=coupon_code,
                # coupon_discount=coupon_discount
            )
            if coupon_id and coupon:

                UserCoupon.objects.update_or_create(

                    user=user,
                    coupon=coupon,

                    defaults={
                        "order": order,
                        "is_used": True
                    }

                )
            random_code = f"DISC-{secrets.token_hex(3).upper()}"
            new_coupon = Coupon.objects.create(
                code=random_code,
                discount=50.00,
                discount_type='fixed',
                valid_from=timezone.now(),
                valid_to=timezone.now() + timedelta(days=7)
            )
            UserCoupon.objects.create(user=user, order=order, coupon=new_coupon)
            request.session['just_earned_coupon'] = new_coupon.code
            request.session.modified = True 
            for item in cart_items:
                if item.product.stock < item.quantity:
                    messages.error(request, f"Only {item.product.stock} stock available for {item.product.name}")
                    return redirect("cart")

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.final_price(),
                    color=item.color,
                    size=item.size
                )

                item.product.stock -= item.quantity
                item.product.save()
            
            cart_items.delete()

        request.session.pop("coupon_id", None)
        request.session.pop("discount", None)

        messages.success(request, "Order placed successfully!")
        return redirect("my_orders")


class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = 'order-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # જો કૂપન જોયા પછી યુઝર પાછો આવે તો સેશન ક્લિયર કરો
        if self.request.GET.get('clear_coupon') == 'true':
            if 'just_earned_coupon' in self.request.session:
                del self.request.session['just_earned_coupon']
        
        context['orders'] = Order.objects.filter(user=self.request.user)\
                                         .select_related('address')\
                                         .prefetch_related('items__product')\
                                         .order_by('-id')
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "order_detail.html"
    context_object_name = "order"

    def get_object(self):
        return get_object_or_404(
            Order,
            id=self.kwargs["pk"],
            user=self.request.user
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": self.object.status})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        order_items = OrderItem.objects.filter(order=order).select_related("product")
        
        total_mrp = order.total_listing_price
            
        subtotal = sum(item.price * item.quantity for item in order_items)

        listing_discount = total_mrp - float(subtotal)
        if listing_discount < 0:
            listing_discount = 0

        expected_grand_total = float(subtotal) + 100
        actual_paid_total = float(order.total_price)

        coupon_discount = expected_grand_total - actual_paid_total
        if coupon_discount < 0:
            coupon_discount = 0

        coupon_code = ""
        if coupon_discount > 0:
            matching_coupon = Coupon.objects.filter(discount=coupon_discount).first()
            
            if matching_coupon:
                coupon_code = matching_coupon.code
            else:
                calculated_percent = round((coupon_discount / expected_grand_total) * 100)
                matching_percent_coupon = Coupon.objects.filter(
                    discount_type='percent', 
                    discount=calculated_percent
                ).first()
                
                if matching_percent_coupon:
                    coupon_code = matching_percent_coupon.code
                else:
                    coupon_code = "Applied"  

        total_savings = float(listing_discount) + float(coupon_discount)

        context["order_items"] = order_items
        context["total_mrp"] = total_mrp
        context["subtotal"] = subtotal
        context["listing_discount"] = listing_discount
        context["coupon_discount"] = coupon_discount
        context["coupon_code"] = coupon_code  
        context["total_savings"] = total_savings
        context["shipping"] = 100 if subtotal > 0 else 0

        return context


class InvoiceView(View):
    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, id=pk, user=request.user)
        
        subtotal = 0.0
        invoice_items = []

        for item in order.items.all():
            item_total = float(item.quantity * item.price)
            subtotal += item_total
            invoice_items.append({
                'product': item.product.name,
                'quantity': item.quantity,
                'price': item.price,
                'total': item_total
            })

        shipping_charge = 100.0
        grand_total = subtotal + shipping_charge

        template = get_template('invoice_pdf.html')
        html = template.render({
            'order': order,
            'invoice_items': invoice_items,
            'subtotal': subtotal,
            'shipping_charge': shipping_charge,
            'grand_total': grand_total
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice-{order.id}.pdf"'
        
        pisa.CreatePDF(html, dest=response)
        return response
    

class AddReviewView(View):

    def post(self, request, pk):

        if not request.user.is_authenticated:
            return redirect('login')

        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        # Only Delivered Orders
        if order.status != "Delivered":
            messages.error(
                request,
                "Review can only be added after delivery."
            )
            return redirect('order_details', pk=order.id)

        # Already Reviewed
        if hasattr(order, 'review'):
            messages.error(
                request,
                "You have already reviewed this order."
            )
            return redirect('order_details', pk=order.id)

        rating = request.POST.get('rating')
        description = request.POST.get('description')

        if not rating:
            messages.error(
                request,
                "Please select rating."
            )
            return redirect('order_details', pk=order.id)

        Review.objects.create(
            order=order,
            user=request.user,
            rating=int(rating),
            description=description
        )

        messages.success(
            request,
            "Review submitted successfully."
        )

        return redirect('order_details', pk=order.id)
    
    
class ReOrderView(LoginRequiredMixin, View):

    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )
        
        for item in order.items.all():
            cart_item = CartItem.objects.filter(
                cart=cart,
                product=item.product,
                color=item.color,
                size=item.size
            ).first()

            if cart_item:
                cart_item.quantity += item.quantity
                cart_item.save()
            else:
                CartItem.objects.create(
                    cart=cart,
                    product=item.product,
                    quantity=item.quantity,
                    color=item.color,
                    size=item.size
                )

        messages.success(
            request,
            "Items prepared for re-order."
        )

        return redirect("checkout")


class CancelOrderView(LoginRequiredMixin, View):

    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        reason = request.POST.get("cancel_reason")
        other_reason = request.POST.get("other_reason")

        if reason == "Other":
            reason = other_reason

        order.status = "Cancelled"
        order.cancel_reason = reason
        order.save()

        messages.success(
            request,
            "Order cancelled successfully."
        )

        return redirect(
            "order_details", 
            pk=order.id
        )
        

class DismissCouponView(LoginRequiredMixin, View):
    def post(self, request):
        if 'just_earned_coupon' in request.session:
            del request.session['just_earned_coupon']
    
        return redirect('checkout')
    
class ApplyCouponView(LoginRequiredMixin, View):

    def post(self, request):

        coupon_id = request.POST.get("coupon_id")

        coupon = get_object_or_404(
            Coupon,
            id=coupon_id
        )

        request.session["coupon_id"] = coupon.id

        messages.success(
            request,
            f"{coupon.code} applied successfully"
        )

        return redirect("checkout")