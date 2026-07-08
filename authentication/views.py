from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from ecom_project.utils import success_response, error_response
from authentication.models import BuyerProfile, SellerProfile, PasswordResetToken
from authentication.serializers import (
    UserRegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    BuyerProfileSerializer,
    SellerProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
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


User = get_user_model()

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid input data.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            # Generate token and store it
            token = uuid.uuid4().hex
            expires_at = timezone.now() + timedelta(minutes=30)
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )

            # Send Email
            subject = "Password Reset Request - Mahi Store"
            message = (
                f"Hello {user.username},\n\n"
                f"You requested a password reset for your account. Please click the link below to reset your password:\n\n"
                f"http://localhost:5173/reset-password?token={token}\n\n"
                f"This link will expire in 30 minutes.\n\n"
                f"If you did not request this, please ignore this email.\n"
            )
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@mahistore.com',
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error or handle it, but still return success to the user
                pass

        # Return generic success message to prevent user enumeration
        return success_response(
            message="If an account with that email exists, we have sent a password reset link.",
            status_code=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid input data.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        token_str = serializer.validated_data['token']
        password = serializer.validated_data['password']

        reset_token = PasswordResetToken.objects.filter(token=token_str).first()

        if not reset_token:
            return error_response(
                message="Invalid or expired token.",
                errors={"token": ["Invalid token."]},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if reset_token.is_used:
            return error_response(
                message="This token has already been used.",
                errors={"token": ["Token already used."]},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if reset_token.expires_at < timezone.now():
            return error_response(
                message="This token has expired.",
                errors={"token": ["Token expired."]},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        user = reset_token.user
        user.set_password(password)
        user.save()

        # Mark token and all other user tokens as used
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        return success_response(
            message="Password reset successfully. You can now login with your new password.",
            status_code=status.HTTP_200_OK
        )



