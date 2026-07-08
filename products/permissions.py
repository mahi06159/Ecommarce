from rest_framework import permissions

class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Custom permission class:
    - Safe methods (GET, HEAD, OPTIONS) are allowed for everyone.
    - Write methods (POST, PUT, PATCH, DELETE) require the user to be authenticated with the role 'Seller'.
    - For product update/delete, the seller must be the owner of that product.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'Seller'
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # If the object is a Product, check that the owner is request.user
        if hasattr(obj, 'seller'):
            return obj.seller == request.user
            
        # If it's a Category (does not have seller), any authenticated Seller is permitted.
        return True
