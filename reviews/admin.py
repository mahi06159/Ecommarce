from django.contrib import admin
from reviews.models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'product', 'rating', 'is_deleted', 'created_at', 'updated_at', 'deleted_at']
    list_filter = ['is_deleted', 'rating', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']

    def get_queryset(self, request):
        return Review.objects.all_with_deleted()

