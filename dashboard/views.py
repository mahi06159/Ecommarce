from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ecom_project.utils import success_response

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
