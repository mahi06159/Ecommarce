from django.urls import path
from products.views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    ProductDropdownListView
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('products/', ProductListCreateView.as_view(), name='product_list_create'),
    path('products/dropdown/', ProductDropdownListView.as_view(), name='product_dropdown_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
