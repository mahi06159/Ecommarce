from django.contrib import admin
from products.models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'seller', 'category', 'price', 'stock', 'is_deleted', 'created_at', 'updated_at', 'deleted_at']
    list_filter = ['is_deleted', 'category', 'seller']
    search_fields = ['name', 'details']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    inlines = [ProductImageInline]

    def get_queryset(self, request):
        return Product.objects.all_with_deleted()

