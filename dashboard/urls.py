from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ====================================
    # DASHBOARD
    # ====================================

    path(
        'dashboard/',
        Dashboardview.as_view(),
        name='dashboard'
    ),

    # ====================================
    # PRODUCT PAGES
    # ====================================

    path(
        'dashboard/add-product/',
        AddProductView.as_view(),
        name='add_product_page'
    ),

    path(
        'dashboard/product-list/',
        ProductlistView.as_view(),
        name='product_list'
    ),

    # ====================================
    # CATEGORY & TYPE PAGES
    # ====================================

    path(
        'dashboard/add-category-page/',
        AddCategoryPageView.as_view(),
        name='add_category_page'
    ),

    path(
        'dashboard/add-type-page/',
        AddTypePageView.as_view(),
        name='add_type_page'
    ),

    # ====================================
    # WISHLIST DASHBOARD
    # ====================================

    path(
        'dashboard/wishlist/',
        WishlistDashboardView.as_view(),
        name='dashboard_wishlist'
    ),

    # ====================================
    # ADMIN CART
    # ====================================

    path(
        'dashboard/cart/',
        AdminCartView.as_view(),
        name='admin_cart'
    ),

    # ====================================
    # USERS
    # ====================================

    path(
        'dashboard/users/',
        UserListView.as_view(),
        name='user-list'
    ),

    path(
    'dashboard/users/',
    UserListView.as_view(),
    name='user_list'
),

path(
    'dashboard/user-edit/<int:pk>/',
    UserEditPageView.as_view(),
    name='user_edit'
),

path(
    'dashboard/api/user/<int:pk>/',
    UserDetailAPI.as_view(),
    name='user_detail_api'
),

path(
    'dashboard/user-delete/<int:pk>/',
    UserDeleteView.as_view(),
    name='user_delete'
),

    # ====================================
    # ADMIN ORDERS
    # ====================================

    path(
        'dashboard/orders/',
        adminOrderListView.as_view(),
        name='order_list'
    ),

    path(
        "dashboard/order/<int:id>/",
        AdminOrderDetailView.as_view(),
        name="order_detail"
    ),

    path(
        'dashboard/order-status/<int:pk>/',
        OrderStatusUpdateView.as_view(),
        name='order_status_update'
    ),
    path(
    'dashboard/order/delete/<int:id>/',
    OrderDeleteView.as_view(),
    name='order_delete'
),
    
    path('api/orders/', OrderListAPI.as_view()),
    path('api/orders/<int:id>/', OrderDetailAPI.as_view()),

    path('api/orders/<int:id>/status/', OrderStatusUpdateAPI.as_view()),

    path('api/orders/<int:id>/delete/', OrderDeleteAPI.as_view()),
    # ====================================
    # CATEGORY API
    # ====================================

    path(
        'api/categories/',
        CategoryListAPI.as_view(),
        name='categories'
    ),

    path(
        'api/category-create/',
        CategoryCreateAPI.as_view(),
        name='category_create_api'
    ),

    path(
        'api/add-category/',
        AddCategoryView.as_view(),
        name='add_category'
    ),

    # ====================================
    # TYPE API
    # ====================================

    path(
        'api/types/<int:category_id>/',
        TypeListAPI.as_view(),
        name='types'
    ),

    path(
        'api/product-type-create/',
        ProductTypeCreateAPI.as_view(),
        name='product_type_create'
    ),

    path(
        'api/add-type/',
        AddTypeView.as_view(),
        name='add_type'
    ),

    # ====================================
    # COLOR & SIZE
    # ====================================

    path(
        'api/add-color/',
        AddColorView.as_view(),
        name='add_color'
    ),

    path(
        'api/add-size/',
        AddSizeView.as_view(),
        name='add_size'
    ),
    path(
        "api/dashboard-login/",
        DashboardLoginAPIView.as_view(),
        name="dashboard_login_api"
    ),
    path(
    "api/dashboard-logout/",
    DashboardLogoutAPIView.as_view(),
    name="dashboard_logout_api"
),
path(
    "dashboard/cancelled-orders/",
    CancelledOrdersTablePage.as_view(),
    name="cancelled_orders_table_page"
),

path(
    "api/cancelled-orders/",
    CancelledOrderListAPI.as_view(),
    name="cancelled_orders_api"
),

    path(
        "cancelled-order-calendar/",
        CancelledOrderCalendarView.as_view(),
        name="cancelled_order_calendar"
    ),

    path(
        "cancelled-order-events/",
        CancelledOrderCalendarEvents.as_view(),
        name="cancelled_order_events"
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)