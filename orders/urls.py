from django.urls import path
from orders.views import (
    AddressListCreateView,
    AddressDetailView,
    OrderListCreateView,
    OrderDetailView,
    OrderItemStatusUpdateView,
    CartView,
    CartItemUpdateDeleteView,
    RazorpayOrderCreateView,
    RazorpayOrderVerifyView
)

urlpatterns = [
    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    path('orders/', OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/items/<int:pk>/status/', OrderItemStatusUpdateView.as_view(), name='order_item_status_update'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('cart/items/<int:pk>/', CartItemUpdateDeleteView.as_view(), name='cart_item_update_delete'),
    path('payments/create/', RazorpayOrderCreateView.as_view(), name='razorpay_order_create'),
    path('payments/verify/', RazorpayOrderVerifyView.as_view(), name='razorpay_order_verify'),
]


