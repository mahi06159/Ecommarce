from django.contrib import admin
from orders.models import Address, Order, OrderItem, Cart, CartItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    fields = ['product', 'product_name', 'quantity', 'price', 'status', 'is_deleted', 'created_at', 'updated_at', 'deleted_at']

    def get_queryset(self, request):
        return OrderItem.objects.all_with_deleted()

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'total_price', 'status', 'shipping_address', 'is_deleted', 'created_at', 'updated_at', 'deleted_at']
    list_filter = ['is_deleted', 'status', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return Order.objects.all_with_deleted()

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'address_line1', 'city', 'state', 'postal_code', 'country', 'is_default', 'is_deleted', 'created_at', 'updated_at', 'deleted_at']
    list_filter = ['is_deleted', 'city', 'state', 'country', 'is_default']
    search_fields = ['user__username', 'address_line1', 'city', 'state']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']

    def get_queryset(self, request):
        return Address.objects.all_with_deleted()

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]



