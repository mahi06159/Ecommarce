from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.models import BuyerProfile, SellerProfile

User = get_user_model()

class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = ['avatar']

class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['store_name', 'store_description', 'store_logo']

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'is_active', 'created_at', 'profile']

    def get_profile(self, obj):
        if obj.role == 'Buyer':
            profile, _ = BuyerProfile.objects.get_or_create(user=obj)
            return BuyerProfileSerializer(profile, context=self.context).data
        elif obj.role == 'Seller':
            profile, _ = SellerProfile.objects.get_or_create(user=obj)
            return SellerProfileSerializer(profile, context=self.context).data
        return None


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone_number']
        extra_kwargs = {
            'role': {'read_only': True}  # Enforced dynamically by the registration endpoints
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if value:
            if User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        role = validated_data.get('role', 'Buyer')
        phone_number = validated_data.get('phone_number', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role,
            phone_number=phone_number
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Embed the user info inside the response JSON
        data['user'] = UserSerializer(self.user).data
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=6, write_only=True)

