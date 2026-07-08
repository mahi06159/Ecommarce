from rest_framework import permissions

class IsBuyerOrReadOnly(permissions.BasePermission):
    """
    Allows read access to anyone (including anonymous users).
    Allows write operations only to authenticated Buyers.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'Buyer'
        )

class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows write operations only to the Buyer who created the review.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.buyer == request.user
