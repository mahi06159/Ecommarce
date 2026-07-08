from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import User, BuyerProfile, SellerProfile

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['id', 'username', 'email', 'role', 'phone_number', 'is_active', 'created_at', 'is_deleted']
    list_filter = UserAdmin.list_filter + ('is_deleted',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number')}),
    )

    def get_queryset(self, request):
        return User.objects.all_with_deleted()

admin.site.register(User, CustomUserAdmin)

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_deleted']
    list_filter = ['is_deleted']
    search_fields = ['user__username']

    def get_queryset(self, request):
        return BuyerProfile.objects.all_with_deleted()

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'store_name', 'is_deleted']
    list_filter = ['is_deleted']
    search_fields = ['user__username', 'store_name']

    def get_queryset(self, request):
        return SellerProfile.objects.all_with_deleted()


