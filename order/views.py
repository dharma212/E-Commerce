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
        buy_now_color = self.request.GET.get('color')
        buy_now_size = self.request.GET.get('size')
        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            qty = int(buy_now_qty) if buy_now_qty else 1
            subtotal = product.final_price() * qty 
            
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
            # CHECK STOCK
            if product.stock < qty:
                messages.error(request, f"Only {product.stock} items available in stock.")
                return redirect("checkout")

            # CREATE ORDER ITEM
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.final_price(),
                color=buy_now_color,
                size=buy_now_size
            )

            # MINUS STOCK
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
            
            order = Order.objects.create(
                user=user, 
                address=order_address, 
                total_price=grand_total, 
                status="Pending"
            )
            
            for item in cart_items:

                # CHECK STOCK
                if item.product.stock < item.quantity:

                    messages.error(
                        request,
                        f"Only {item.product.stock} stock available for {item.product.name}"
                    )

                    return redirect("cart")

                # CREATE ORDER ITEM
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.final_price(),
                    color=item.color,
                    size=item.size
                )

                # MINUS STOCK
                item.product.stock -= item.quantity
                item.product.save()
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
            return JsonResponse({
                "status": self.object.status,
            })

        return super().get(request, *args, **kwargs)

# views.py

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from datetime import datetime


from django.views import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

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

        # શિપિંગ ચાર્જ અને ગ્રાન્ડ ટોટલની ગણતરી
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
    
# views.py

from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages



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
    
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# views.py

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

        # Re-order કરતી વખતે જો જૂનું કાર્ટ ખાલી કરવું હોય તો નીચેની લાઇન અન-કમેન્ટ કરો:
        # CartItem.objects.filter(cart=cart).delete()

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

        # કાર્ટમાં મોકલવાને બદલે સીધું જ CHECKOUT વ્યુ પર મોકલો!
        return redirect("checkout") # તમારી url pattern નું નામ 'checkout' હોવું જોઈએ


class CancelOrderView(LoginRequiredMixin, View):

    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        reason = request.POST.get("cancel_reason")
        other_reason = request.POST.get("other_reason")

        # જો યુઝરે રેડિયો બટનમાં "Other" સિલેક્ટ કર્યું હોય તો ટેક્સ્ટ બોક્સની વેલ્યુ લો
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
            "order_details", # તમારા ઓર્ડર ડિટેલના url નેમ મુજબ રાખવું (pk=order.id સાથે)
            pk=order.id
        )