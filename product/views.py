from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from User.models import *
from User.serializers import ProductSerializer

class SearchProductView(View):

    def get(self, request, *args, **kwargs):

        search = request.GET.get("search", "")

        products = Product.objects.filter(
            name__icontains=search
        )[:8]

        product_list = []

        for product in products:

            # GET FIRST IMAGE
            first_image = product.images.first()

            # IMAGE URL
            if first_image and first_image.image:
                image_url = first_image.image.url
            else:
                image_url = "/static/img/no-image.png"

            product_list.append({

                "id": product.id,

                "name": product.name,

                "price": str(product.final_price()),

                "image": image_url,

            })

        return JsonResponse({

            "products": product_list

        })


# ====================================
# Shop View
# ====================================
class ShopView(TemplateView):

    template_name = "shop.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        products = Product.objects.all().order_by("-id")

        # =========================
        # FILTERS
        # =========================

        category = self.request.GET.get("category")
        type_id = self.request.GET.get("type")
        color = self.request.GET.get("color")
        size = self.request.GET.get("size")

        min_price = self.request.GET.get("min")
        max_price = self.request.GET.get("max")

        sort = self.request.GET.get("sort")

        # CATEGORY
        if category:
            products = products.filter(
                category_id=category
            )

        # TYPE
        if type_id:
            products = products.filter(
                type_id=type_id
            )

        # COLOR
        if color:
            products = products.filter(
                color_id=color
            )

        # SIZE
        if size:
            products = products.filter(
                size_id=size
            )

        # =========================
        # PRICE FILTER
        # =========================

        filtered_products = []

        for product in products:

            final_price = product.final_price()

            # MIN PRICE
            if min_price:

                if final_price < int(min_price):
                    continue

            # MAX PRICE
            if max_price:

                if final_price > int(max_price):
                    continue

            filtered_products.append(product)

        products = filtered_products

        # =========================
        # SORTING
        # =========================

        if sort == "low":

            products = sorted(
                products,
                key=lambda x: x.final_price()
            )

        elif sort == "high":

            products = sorted(
                products,
                key=lambda x: x.final_price(),
                reverse=True
            )

        # =========================
        # PAGINATION
        # =========================

        paginator = Paginator(products, 9)

        page_number = self.request.GET.get("page")

        page_obj = paginator.get_page(page_number)

        # =========================
        # CART PRODUCTS
        # =========================

        cart_product_ids = []

        wishlist_product_ids = []

        if self.request.user.is_authenticated:

            cart_product_ids = list(

                CartItem.objects.filter(
                    cart__user=self.request.user
                ).values_list(
                    "product_id",
                    flat=True
                )

            )

            wishlist_product_ids = list(

                Wishlist.objects.filter(
                    user=self.request.user
                ).values_list(
                    "product_id",
                    flat=True
                )

            )

        # =========================
        # CONTEXT
        # =========================

        context["products"] = page_obj.object_list

        context["page_obj"] = page_obj

        context["categories"] = Category.objects.all()

        context["types"] = ProductType.objects.all()

        context["colors"] = Color.objects.all()

        context["sizes"] = Size.objects.all()

        context["cart_product_ids"] = cart_product_ids

        context["wishlist_product_ids"] = wishlist_product_ids

        return context

    # =========================
    # AJAX
    # =========================

    def get(self, request, *args, **kwargs):

        context = self.get_context_data()

        return self.render_to_response(context)


class ProductDetailView(View):

    def get(self, request, id):

        # =========================
        # PRODUCT
        # =========================

        product = get_object_or_404(
            Product,
            id=id
        )

        # =========================
        # RELATED PRODUCTS
        # =========================

        related_products = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        )[:8]

        # =========================
        # DEFAULT VALUES
        # =========================

        in_cart = False

        in_wishlist = False

        cart_quantity = 1

        cart_product_ids = []

        wishlist_product_ids = []

        # =========================
        # LOGIN USER
        # =========================

        if request.user.is_authenticated:

            # =========================
            # CART ITEM
            # =========================

            cart_item = CartItem.objects.filter(

                cart__user=request.user,

                product=product

            ).first()

            # PRODUCT IN CART
            if cart_item:

                in_cart = True

                cart_quantity = cart_item.quantity

            # =========================
            # ALL CART PRODUCTS
            # =========================

            cart_product_ids = list(

                CartItem.objects.filter(

                    cart__user=request.user

                ).values_list(

                    "product_id",

                    flat=True

                )

            )

            # =========================
            # WISHLIST PRODUCTS
            # =========================

            wishlist_product_ids = list(

                Wishlist.objects.filter(

                    user=request.user

                ).values_list(

                    "product_id",

                    flat=True

                )

            )

            # PRODUCT IN WISHLIST
            in_wishlist = product.id in wishlist_product_ids

        # =========================
        # CONTEXT
        # =========================

        context = {

            "product": product,

            "related_products": related_products,

            "in_cart": in_cart,

            "in_wishlist": in_wishlist,

            "cart_quantity": cart_quantity,

            "cart_product_ids": cart_product_ids,

            "wishlist_product_ids": wishlist_product_ids

        }

        return render(

            request,

            "detail.html",

            context

        )


class ProductListAPI(APIView):

    def get(self, request):

        products = Product.objects.all().order_by('-id')

        data = []

        for p in products:

            mrp = float(p.mrp or 0)

            discount = float(p.discount or 0)

            final_price = float(p.mrp) - float(p.discount)

            discount_percent = 0

            if float(p.mrp) > 0:

                discount_percent = round(
                    (float(p.discount) / float(p.mrp)) * 100,
                    2
                )

            data.append({

                "id": p.id,

                "name": p.name,

                "mrp": p.mrp,

                "discount": p.discount,

                "final_price": final_price,

                "discount_percent": discount_percent,

                "stock": p.stock,

                "description": p.description,

                # IDS
                "category_id": p.category.id if p.category else "",

                "type_id": p.type.id if p.type else "",

                "color_id": p.color.id if p.color else "",

                "size_id": p.size.id if p.size else "",

                # NAMES
                "category_name": p.category.name if p.category else "",

                "type_name": p.type.name if p.type else "",

                "color_name": p.color.name if p.color else "",

                "size_name": p.size.name if p.size else "",

                # IMAGES
                "images": [

                    {
                        "image": img.image.url
                    }

                    for img in p.images.all()

                ]

            })

        return Response(data)

from rest_framework import status
class ProductDeleteAPI(APIView):

    def delete(self, request, pk):

        try:

            product = Product.objects.get(id=pk)

            product.delete()

            return Response({
                "success": True,
                "message": "Product deleted successfully"
            })

        except Product.DoesNotExist:

            return Response({
                "success": False,
                "message": "Product not found"
            }, status=status.HTTP_404_NOT_FOUND)
           

class ProductUpdateAPI(APIView):

    def patch(self, request, pk):

        try:

            product = Product.objects.get(id=pk)

        except Product.DoesNotExist:

            return Response({
                "success": False,
                "message": "Product not found"
            }, status=404)

        data = request.data

        product.name = data.get("name", product.name)
        product.stock = data.get("stock", product.stock)
        product.discount = data.get("discount", product.discount)

        product.save()

        return Response({
            "success": True,
            "message": "Product updated successfully"
        })

class ProductCreateAPI(APIView):

    parser_classes = [MultiPartParser, FormParser]

    # =========================================
    # GET SINGLE PRODUCT FOR EDIT
    # =========================================
    def get(self, request):

        product_id = request.GET.get("id")

        # NORMAL ADD PRODUCT PAGE
        if not product_id:

            return Response({
                "edit": False
            })

        try:

            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:

            return Response({
                "success": False,
                "message": "Product not found"
            }, status=404)

        return Response({

            "edit": True,

            "id": product.id,

            "name": product.name,

            "mrp": product.mrp,

            "discount": product.discount,

            "stock": product.stock,

            "description": product.description,

            # CATEGORY
            "category": product.category.id if product.category else "",
            "category_name": product.category.name if product.category else "",

            # TYPE
            "type": product.type.id if product.type else "",
            "type_name": product.type.name if product.type else "",

            # COLOR
            "color": product.color.id if product.color else "",
            "color_name": product.color.name if product.color else "",

            # SIZE
            "size": product.size.id if product.size else "",
            "size_name": product.size.name if product.size else "",

            # IMAGES
            "images": [

                {
                    "id": img.id,
                    "image": img.image.url
                }

                for img in product.images.all()

            ]

        })


    # =========================================
    # ADD PRODUCT
    # =========================================
    def post(self, request):

        try:

            serializer = ProductSerializer(data=request.data)

            if serializer.is_valid():

                # SAVE PRODUCT
                product = serializer.save()

                # SAVE IMAGES
                images = request.FILES.getlist('images')

                for img in images:

                    ProductImage.objects.create(
                        product=product,
                        image=img
                    )

                return Response(
                    {
                        "success": True,
                        "message": "Product added successfully"
                    },
                    status=201
                )

            return Response(
                serializer.errors,
                status=400
            )

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=500
            )


    # =========================================
    # UPDATE PRODUCT
    # =========================================
    def patch(self, request):

        try:

            product_id = request.data.get("id")

            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:

            return Response({
                "success": False,
                "message": "Product not found"
            }, status=404)

        try:

            # UPDATE FIELDS
            product.name = request.data.get("name")
            product.mrp = request.data.get("mrp")
            product.discount = request.data.get("discount")
            product.stock = request.data.get("stock")
            product.description = request.data.get("description")

            # CATEGORY
            category_id = request.data.get("category")

            if category_id:
                product.category_id = category_id

            # TYPE
            type_id = request.data.get("type")

            if type_id:
                product.type_id = type_id

            # COLOR
            color_id = request.data.get("color")

            if color_id:
                product.color_id = color_id

            # SIZE
            size_id = request.data.get("size")

            if size_id:
                product.size_id = size_id

            product.save()

            # NEW IMAGES
            images = request.FILES.getlist("images")

            if images:

                # DELETE OLD
                product.images.all().delete()

                # ADD NEW
                for img in images:

                    ProductImage.objects.create(
                        product=product,
                        image=img
                    )

            return Response({

                "success": True,
                "message": "Product updated successfully"

            })

        except Exception as e:

            return Response({

                "success": False,
                "message": str(e)

            }, status=500)

class detailview(TemplateView):

    template_name = "detail.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        product = Product.objects.get(
            id=self.kwargs["pk"]
        )

        related_products = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        )[:8]

        # MAIN PRODUCT CART
        in_cart = False

        # MAIN PRODUCT WISHLIST
        in_wishlist = False

        # RELATED PRODUCTS
        cart_product_ids = []
        wishlist_product_ids = []

        if self.request.user.is_authenticated:

            # CART
            cart = Cart.objects.filter(
                user=self.request.user
            ).first()

            if cart:

                cart_product_ids = list(

                    CartItem.objects.filter(
                        cart=cart
                    ).values_list(
                        "product_id",
                        flat=True
                    )

                )

                in_cart = product.id in cart_product_ids

            # WISHLIST
            wishlist_product_ids = list(

                Wishlist.objects.filter(
                    user=self.request.user
                ).values_list(
                    "product_id",
                    flat=True
                )

            )

            in_wishlist = product.id in wishlist_product_ids

        context["product"] = product

        context["related_products"] = related_products

        context["in_cart"] = in_cart

        context["in_wishlist"] = in_wishlist

        context["cart_product_ids"] = cart_product_ids

        context["wishlist_product_ids"] = wishlist_product_ids

        return context
    
from django.views import View

class BuyNowAPI(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "message": "Please login first"}, status=401)

        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({
            "success": True,
            "redirect_url": "/checkout/"  
        })