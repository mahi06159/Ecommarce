import datetime
from django.utils import timezone
from django.db.models import Sum, F, Q, Count, DecimalField
from django.db.models.functions import TruncMonth
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from ecom_project.utils import success_response, error_response
from products.models import Product
from orders.models import Order, OrderItem

class DashboardView(APIView):
    """
    GET: Returns a catalog of available API endpoints across all application modules.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        links = {
            "Authentication": {
                "Register Buyer": "/api/auth/register/buyer/",
                "Register Seller": "/api/auth/register/seller/",
                "Login": "/api/auth/login/",
                "Refresh Token": "/api/auth/token/refresh/",
                "Logout": "/api/auth/logout/",
                "Profile": "/api/auth/profile/"
            },
            "Addresses": {
                "Addresses": "/api/addresses/",
                "Address Detail": "/api/addresses/<id>/"
            },
            "Cart": {
                "Cart Get/Add": "/api/cart/",
                "Cart Item Update/Delete": "/api/cart/items/<id>/"
            },
            "Products": {
                "Categories": "/api/categories/",
                "Category Detail": "/api/categories/<id>/",
                "Products": "/api/products/",
                "Product Detail": "/api/products/<id>/"
            },
            "Orders": {
                "Orders": "/api/orders/",
                "Order Detail": "/api/orders/<id>/",
                "Order Item Status Update": "/api/orders/items/<id>/status/"
            },
            "Reviews": {
                "Reviews": "/api/reviews/",
                "Review Detail": "/api/reviews/<id>/"
            }
        }

        return success_response(
            message="E-Commerce API Directory dashboard retrieved.",
            data=links
        )


class SellerStatsView(APIView):
    """
    GET: Returns real-time seller analytics (revenue, orders count, product counts, trend, top products).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        seller = request.user
        if seller.role != 'Seller':
            return error_response(
                message="Access denied. Seller accounts only. 🌸",
                status_code=status.HTTP_403_FORBIDDEN
            )

        # 1. Total revenue (sum of price*quantity for seller's order items where payment is Paid or order is Completed, excluding Cancelled items)
        revenue_data = OrderItem.objects.filter(
            product__seller=seller
        ).filter(
            Q(order__status='Completed') | Q(order__payments__status='Paid')
        ).exclude(
            status='Cancelled'
        ).aggregate(
            total=Sum(F('price') * F('quantity'), output_field=DecimalField())
        )
        total_revenue = float(revenue_data['total'] or 0.00)

        # 2. Total orders (distinct count of orders containing seller's products)
        total_orders = Order.objects.filter(
            items__product__seller=seller
        ).distinct().count()

        # 3. Pending orders count (distinct count of orders containing seller's products with status Pending)
        pending_orders_count = Order.objects.filter(
            items__product__seller=seller,
            status='Pending'
        ).distinct().count()

        # 4. Total products count
        total_products = Product.objects.filter(seller=seller).count()

        # 5. Low stock products (stock < 5)
        low_stock_products = Product.objects.filter(seller=seller, stock__lt=5).count()

        # 6. Top 5 selling products (by quantity sold, excluding Cancelled items)
        top_5 = OrderItem.objects.filter(
            product__seller=seller
        ).filter(
            Q(order__status='Completed') | Q(order__payments__status='Paid')
        ).exclude(
            status='Cancelled'
        ).values(
            'product__id', 'product__name'
        ).annotate(
            total_qty=Sum('quantity'),
            total_sales=Sum(F('price') * F('quantity'), output_field=DecimalField())
        ).order_by('-total_qty')[:5]

        top_5_selling_products = []
        for item in top_5:
            top_5_selling_products.append({
                "product_id": item['product__id'],
                "product_name": item['product__name'],
                "quantity_sold": item['total_qty'],
                "total_sales": float(item['total_sales'] or 0.00)
            })

        # 7. Monthly revenue trend (last 6 months, grouped by month)
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        monthly_trend = OrderItem.objects.filter(
            product__seller=seller,
            created_at__gte=six_months_ago
        ).filter(
            Q(order__status='Completed') | Q(order__payments__status='Paid')
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            revenue=Sum(F('price') * F('quantity'), output_field=DecimalField())
        ).order_by('month')

        trend_data = []
        for item in monthly_trend:
            if item['month']:
                month_str = item['month'].strftime('%b %Y') # e.g. "Jul 2026"
                trend_data.append({
                    "month": month_str,
                    "revenue": float(item['revenue'] or 0)
                })

        # Return stats
        data = {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "pending_orders_count": pending_orders_count,
            "total_products": total_products,
            "low_stock_products": low_stock_products,
            "top_5_selling_products": top_5_selling_products,
            "monthly_revenue_trend": trend_data
        }

        return success_response(
            message="Seller stats retrieved successfully.",
            data=data,
            status_code=status.HTTP_200_OK
        )
