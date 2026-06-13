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
import json

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


from django.views import View
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg, Count

class ProductDetailView(View):

    def get(self, request, slug):

        # =========================
        # PRODUCT
        # =========================
        product = get_object_or_404(
            Product,
            slug=slug
        )
        
        reviews = Review.objects.filter(
            order__items__product=product
        ).select_related("user").distinct().order_by("-created_at")

        avg_rating = reviews.aggregate(
            Avg('rating')
        )['rating__avg'] or 0

        avg_rating = round(avg_rating, 1)

        total_reviews = reviews.count()
        
        rating_breakdown = {
            5: reviews.filter(rating=5).count(),
            4: reviews.filter(rating=4).count(),
            3: reviews.filter(rating=3).count(),
            2: reviews.filter(rating=2).count(),
            1: reviews.filter(rating=1).count(),
        }

        # ====================================
        # PREVIOUS AND NEXT PRODUCT NAVIGATION
        # ====================================
        category_products = Product.objects.filter(category=product.category)
        
        previous_product = category_products.filter(
            created_at__lt=product.created_at
        ).order_by('-created_at').first()
        
        next_product = category_products.filter(
            created_at__gt=product.created_at
        ).order_by('created_at').first()

        # =========================
        # RELATED PRODUCTS (Fixed Query Path)
        # =========================
        # This isolates related items safely without trying to look up missing 'order' paths
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

            in_wishlist = product.id in wishlist_product_ids

        # =========================
        # CONTEXT
        # =========================
        color_images = {}

        for img in product.images.all():
            color = getattr(img.color, "name", "").lower()

            if color not in color_images:
                color_images[color] = []

            color_images[color].append(img.image.url)

        context = {
            "product": product,
            "previous_product": previous_product,
            "next_product": next_product,
            "related_products": related_products,
            "in_cart": in_cart,
            "in_wishlist": in_wishlist,
            "cart_quantity": cart_quantity,
            "cart_product_ids": cart_product_ids,
            "wishlist_product_ids": wishlist_product_ids,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "total_reviews": total_reviews,
            "rating_breakdown": rating_breakdown,
            "color_images": color_images
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

            final_price = float(p.mrp or 0) - float(p.discount or 0)

            discount_percent = 0

            if float(p.mrp or 0) > 0:

                discount_percent = round(
                    (float(p.discount or 0) / float(p.mrp or 0)) * 100,
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

                # CATEGORY + TYPE
                "category_id": p.category.id if p.category else "",

                "type_id": p.type.id if p.type else "",

                "category_name": p.category.name if p.category else "",

                "type_name": p.type.name if p.type else "",

                # MULTIPLE COLORS
                "colors": [

                    {
                        "id": color.id,
                        "name": color.name
                    }

                    for color in p.colors.all()

                ],

                # MULTIPLE SIZES
                "sizes": [

                    {
                        "id": size.id,
                        "name": size.name
                    }

                    for size in p.sizes.all()

                ],

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

            "is_featured": product.is_featured,

            # CATEGORY
            "category": product.category.id if product.category else "",
            "category_name": product.category.name if product.category else "",

            # TYPE
            "type": product.type.id if product.type else "",
            "type_name": product.type.name if product.type else "",

            # COLOR
            "colors": [

                {
                    "id": c.id,
                    "name": c.name
                }

                for c in product.colors.all()

            ],

            # SIZE
            "sizes": [

                {
                    "id": s.id,
                    "name": s.name
                }

                for s in product.sizes.all()

            ],            
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
                product = serializer.save()

                # FEATURED
                product.is_featured = (request.data.get("is_featured") == "true")
                product.save()

                # MULTIPLE COLORS
                colors = request.data.getlist("colors")
                if colors:
                    product.colors.set(colors)

                # MULTIPLE SIZES
                sizes = request.data.getlist("sizes")
                if sizes:
                    product.sizes.set(sizes)

                images = request.FILES.getlist("images")
                image_colors = request.data.getlist("image_colors")  
                image_sizes = request.data.getlist("image_sizes")    

                for index, img in enumerate(images):
                    img_color_id = image_colors[index] if index < len(image_colors) else None
                    img_size_id = image_sizes[index] if index < len(image_sizes) else None
                    if img_color_id == "" or img_color_id == "null": img_color_id = None
                    if img_size_id == "" or img_size_id == "null": img_size_id = None

                    ProductImage.objects.create(
                        product=product,
                        image=img,
                        color_id=img_color_id,  
                        size_id=img_size_id     
                    )

                return Response({
                    "success": True,
                    "message": "Product added successfully"
                }, status=201)

            return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=500)

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
            # =====================================
            # UPDATE FIELDS
            # =====================================
            product.name = request.data.get("name", product.name)
            product.mrp = request.data.get("mrp", product.mrp)
            product.discount = request.data.get("discount", product.discount)
            product.stock = request.data.get("stock", product.stock)
            product.description = request.data.get("description", product.description)

            # =====================================
            # FEATURED
            # =====================================
            product.is_featured = (request.data.get("is_featured") == "true")

            # =====================================
            # CATEGORY
            # =====================================
            category_id = request.data.get("category")
            if category_id:
                product.category_id = category_id

            # =====================================
            # TYPE
            # =====================================
            type_id = request.data.get("type")
            if type_id:
                product.type_id = type_id

            # ================================
            # COLORS (SAFE FIX)
            # ================================
            color_ids = request.data.getlist("colors")
            clean_color_ids = []
            for c in color_ids:
                try:
                    clean_color_ids.append(int(c))
                except:
                    try:
                        obj = json.loads(c)
                        clean_color_ids.append(int(obj["id"]))
                    except:
                        pass

            if clean_color_ids:
                product.colors.set(clean_color_ids)

            # ================================
            # SIZES (SAFE FIX)
            # ================================
            size_ids = request.data.getlist("sizes")
            clean_size_ids = []
            for s in size_ids:
                try:
                    clean_size_ids.append(int(s))
                except:
                    try:
                        obj = json.loads(s)
                        clean_size_ids.append(int(obj["id"]))
                    except:
                        pass

            if clean_size_ids:
                product.sizes.set(clean_size_ids)

            product.save()

            # =====================================
            # UPDATE IMAGES WITH COLOR & SIZE (FIXED)
            # =====================================
            images = request.FILES.getlist("images")
            
            image_colors = request.data.getlist("image_colors")  
            image_sizes = request.data.getlist("image_sizes")    

            if images:
                product.images.all().delete()

                for index, img in enumerate(images):
                    img_color_id = image_colors[index] if index < len(image_colors) else None
                    img_size_id = image_sizes[index] if index < len(image_sizes) else None
                    
                    if img_color_id == "" or img_color_id == "null": img_color_id = None
                    if img_size_id == "" or img_size_id == "null": img_size_id = None

                    ProductImage.objects.create(
                        product=product,
                        image=img,
                        color_id=img_color_id,   
                        size_id=img_size_id      
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

        product = get_object_or_404(Product, slug=product_id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({
            "success": True,
            "redirect_url": "/checkout/"  
        })