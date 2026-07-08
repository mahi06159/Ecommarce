from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from ecom_project.utils import success_response, error_response
from authentication.models import BuyerProfile, SellerProfile
from authentication.serializers import (
    UserRegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    BuyerProfileSerializer,
    SellerProfileSerializer
)
from rest_framework_simplejwt.serializers import TokenRefreshSerializer



class BuyerRegistrationView(APIView):
    """
    API view for Buyer registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role='Buyer')
            return success_response(
                message="Buyer registered successfully.",
                data=UserSerializer(user).data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Registration failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class SellerRegistrationView(APIView):
    """
    API view for Seller registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role='Seller')
            return success_response(
                message="Seller registered successfully.",
                data=UserSerializer(user).data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Registration failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT Obtain View returning custom JSON wrapper.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Instantiate the custom token serializer directly for clarity and beginner-friendliness
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(
            message="Login successful.",
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK
        )

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT Refresh View returning custom JSON wrapper.
    """
    def post(self, request, *args, **kwargs):
        # Instantiate the token refresh serializer directly for clarity and beginner-friendliness
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(
            message="Token refreshed successfully.",
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    API view to blacklist refresh token on logout.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return error_response(
                message="Refresh token is required.",
                errors={"refresh": ["This field is required."]},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(
                message="Logout successful (token blacklisted).",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response(
                message="Invalid or blacklisted token.",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )

class ProfileView(APIView):
    """
    API view to get or update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return success_response(
            message="Profile fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def patch(self, request):
        user = request.user
        
        # Optionally update user fields (e.g. email)
        user_serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if not user_serializer.is_valid():
            return error_response(
                message="Profile update failed.",
                errors=user_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        user_serializer.save()
        
        # Update role-specific profile fields if profile data is provided
        profile_data = request.data.get('profile')
        if profile_data:
            if user.role == 'Buyer':
                profile, _ = BuyerProfile.objects.get_or_create(user=user)
                profile_serializer = BuyerProfileSerializer(profile, data=profile_data, partial=True)
            elif user.role == 'Seller':
                profile, _ = SellerProfile.objects.get_or_create(user=user)
                profile_serializer = SellerProfileSerializer(profile, data=profile_data, partial=True)
            else:
                profile_serializer = None
                
            if profile_serializer:
                if not profile_serializer.is_valid():
                    return error_response(
                        message="Profile update failed.",
                        errors=profile_serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                profile_serializer.save()

        full_serializer = UserSerializer(user, context={'request': request})
        return success_response(
            message="Profile updated successfully.",
            data=full_serializer.data,
            status_code=status.HTTP_200_OK
        )

    def delete(self, request):
        user = request.user
        user.delete()
        return success_response(
            message="User account deleted successfully.",
            status_code=status.HTTP_200_OK
        )


