from django.urls import path
from dashboard.views import DashboardView, SellerStatsView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='api_dashboard'),
    path('dashboard/seller-stats/', SellerStatsView.as_view(), name='seller_stats'),
]
