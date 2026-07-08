from rest_framework import serializers
from reviews.models import Review
from authentication.serializers import UserSerializer
from products.models import Product

class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all_with_deleted())
    buyer = UserSerializer(read_only=True)

    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'buyer',
            'product',
            'product_name',
            'rating',
            'comment',
            'created_at'
        ]
        read_only_fields = ['buyer']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be an integer between 1 and 5 inclusive.")
        return value

    def validate_product(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("Cannot review a deleted product.")
        return value
