from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status

def success_response(message, data=None, status_code=status.HTTP_200_OK):
    """
    Returns a unified success response layout.
    """
    return Response({
        "success": True,
        "message": message,
        "data": data or {}
    }, status=status_code)

def error_response(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a unified error response layout.
    """
    return Response({
        "success": False,
        "message": message,
        "errors": errors or {}
    }, status=status_code)

from rest_framework_simplejwt.exceptions import TokenError

def custom_exception_handler(exc, context):
    """
    Custom exception handler to format DRF exceptions to follow:
    {
        "success": False,
        "message": "...",
        "errors": { ... }
    }
    """
    # Intercept SimpleJWT TokenError (such as blacklisted/expired token errors)
    if isinstance(exc, TokenError):
        return Response({
            "success": False,
            "message": str(exc),
            "errors": {"detail": str(exc)}
        }, status=status.HTTP_401_UNAUTHORIZED)

    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data
        message = "An error occurred."
        
        if isinstance(errors, dict):
            if "detail" in errors:
                message = str(errors["detail"])
            else:
                message = "Validation failed."
        elif isinstance(errors, list):
            if len(errors) > 0:
                message = str(errors[0])
        else:
            message = str(errors)

        response.data = {
            "success": False,
            "message": message,
            "errors": errors
        }

    return response
