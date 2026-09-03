from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views


urlpatterns = [

    # =========================
    # HOME
    # =========================

    path(
        '',
        views.home,
        name='home'
    ),


    # =========================
    # PRODUCTS
    # =========================

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),

    path(
        'product/<int:product_id>/review/',
        views.add_review,
        name='add_review'
    ),


    # =========================
    # CART
    # =========================

    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/',
        views.cart,
        name='cart'
    ),

    path(
        'cart/remove/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'cart/update/<int:item_id>/',
        views.update_cart,
        name='update_cart'
    ),


    # =========================
    # ORDERS
    # =========================

    path(
        'order/place/',
        views.place_order,
        name='place_order'
    ),

    path(
        'orders/',
        views.order_history,
        name='order_history'
    ),

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),


    # =========================
    # AUTHENTICATION
    # =========================

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),


    # =========================
    # ADMIN DASHBOARD
    # =========================

    path(
        'dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),


    # =========================
    # DJANGO ADMIN
    # =========================

    path(
        'admin/',
        admin.site.urls
    ),
]


# =========================
# MEDIA FILES
# =========================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )


urlpatterns += [
    path(
        'dashboard/products/',
        views.admin_products,
        name='admin_products'
    ),

    path(
        'dashboard/products/add/',
        views.admin_add_product,
        name='admin_add_product'
    ),

    path(
        'dashboard/products/<int:product_id>/edit/',
        views.admin_edit_product,
        name='admin_edit_product'
    ),

    path(
        'dashboard/products/<int:product_id>/delete/',
        views.admin_delete_product,
        name='admin_delete_product'
    ),
]