from django.contrib import admin
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Review)
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

    list_filter = ('status',)

    search_fields = ('name', 'phone', 'address')