from django.urls import path
from authentication.views import (
    BuyerRegistrationView,
    SellerRegistrationView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    ProfileView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

urlpatterns = [
    path('register/buyer/', BuyerRegistrationView.as_view(), name='buyer_register'),
    path('register/seller/', SellerRegistrationView.as_view(), name='seller_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
