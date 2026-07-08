from django.urls import path
from reviews.views import (
    ReviewListCreateView,
    ReviewDetailView
)

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view(), name='review_list_create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
]
