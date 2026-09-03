from django.contrib import admin
from .models import (
    Product,
    Category,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
)


# =========================
# CATEGORY
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )

    search_fields = (
        'name',
    )


# =========================
# PRODUCT
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'category',
        'price',
        'stock',
        'created_at',
    )

    list_filter = (
        'category',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    list_editable = (
        'price',
        'stock',
    )

    ordering = (
        '-created_at',
    )


# =========================
# CART
# =========================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'session_key',
        'created_at',
    )

    search_fields = (
        'session_key',
    )


# =========================
# CART ITEM
# =========================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cart',
        'product',
        'quantity',
    )

    list_filter = (
        'product',
    )

    search_fields = (
        'product__name',
    )


# =========================
# ORDER
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'phone',
        'total_price',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'name',
        'phone',
        'address',
    )

    list_editable = (
        'status',
    )

    ordering = (
        '-created_at',
    )


# =========================
# ORDER ITEM
# =========================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
    )

    search_fields = (
        'product__name',
    )


# =========================
# REVIEW
# =========================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product',
        'user',
        'rating',
        'created_at',
    )

    list_filter = (
        'rating',
        'created_at',
    )

    search_fields = (
        'product__name',
        'user__username',
        'comment',
    )

    ordering = (
        '-created_at',
    )