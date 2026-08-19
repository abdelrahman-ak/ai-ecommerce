from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views


urlpatterns = [
    path('', views.home, name='home'),

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),

    path(
        'cart/add/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path('cart/', views.cart, name='cart'),

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

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('checkout/', views.checkout, name='checkout'),

    path(
        'product/<int:product_id>/review/',
        views.add_review,
        name='add_review'
    ),

    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )