from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from User.models import *

class checkoutview(LoginRequiredMixin, TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        buy_now_id = self.request.GET.get('buy_now')
        buy_now_qty = self.request.GET.get('qty')

        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            qty = int(buy_now_qty) if buy_now_qty else 1
            subtotal = product.final_price() * qty 
            
            context["cart_items"] = [{
                'product': product,
                'quantity': qty,
                'total_price': subtotal
            }]
            context["buy_now_id"] = buy_now_id
            context["buy_now_qty"] = qty
        else:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_items = CartItem.objects.filter(cart=cart).select_related("product")
            subtotal = sum(item.total_price for item in cart_items) if cart_items.exists() else 0
            context["cart_items"] = cart_items

        shipping = 100 if subtotal > 0 else 0
        context["subtotal"] = subtotal
        context["shipping"] = shipping
        context["grand_total"] = subtotal + shipping
        
        default_addr = Address.objects.filter(user=user, is_default=True).first()
        if not default_addr:
            default_addr = Address.objects.filter(user=user).first()
            
        context["default_address"] = default_addr
        context["addresses"] = Address.objects.filter(user=user)
        context["profile"] = Profile.objects.filter(user=user).first()
        
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        buy_now_id = request.POST.get("buy_now_id")
        buy_now_qty = request.POST.get("buy_now_qty")
        payment_method = request.POST.get("payment")
        selected_address_id = request.POST.get("selected_address") 

        if selected_address_id:
            order_address = get_object_or_404(Address, id=selected_address_id, user=user)
        else:
            order_address = Address.objects.filter(user=user, is_default=True).first() or Address.objects.filter(user=user).first()

        if not order_address:
            messages.error(request, "Please add a delivery address first.")
            return redirect("add_address")

        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            qty = int(buy_now_qty)
            total = (product.final_price() * qty) + 100 
            
            order = Order.objects.create(
                user=user, 
                address=order_address, 
                total_price=total, 
                status="Pending",
                payment_method=payment_method 
            )
            OrderItem.objects.create(
                order=order, product=product, quantity=qty, price=product.final_price()
            )
        else:
            # --- CART ORDER ---
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            if not cart_items.exists():
                return redirect("cart")

            subtotal = sum(item.total_price for item in cart_items)
            grand_total = subtotal + 100
            
            order = Order.objects.create(
                user=user, 
                address=order_address, 
                total_price=grand_total, 
                status="Pending"
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order, product=item.product, 
                    quantity=item.quantity, price=item.product.final_price()
                )
            cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect("my_orders")


class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = 'order-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user)\
                                         .select_related('address')\
                                         .prefetch_related('items__product')\
                                         .order_by('-id')

        return context


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "order_details.html"
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
            return JsonResponse({
                "status": self.object.status,
            })

        return super().get(request, *args, **kwargs)
