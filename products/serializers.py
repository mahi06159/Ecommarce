from rest_framework import serializers
from products.models import Category, Product, ProductImage
from authentication.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def validate_name(self, value):
        if Category.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'order']

class ProductInputSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    delete_image_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = ['category', 'name', 'details', 'price', 'stock', 'uploaded_images', 'delete_image_ids']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive decimal.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        validated_data.pop('delete_image_ids', None)
        product = Product.objects.create(**validated_data)
        
        for idx, img in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=img,
                is_primary=(idx == 0),
                order=idx
            )
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        delete_image_ids = validated_data.pop('delete_image_ids', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if delete_image_ids:
            ProductImage.objects.filter(product=instance, id__in=delete_image_ids).delete()

        if uploaded_images:
            existing_images = instance.images.all()
            has_primary = existing_images.filter(is_primary=True).exists()
            start_order = (existing_images.order_by('-order').first().order + 1) if existing_images.exists() else 0
            
            for idx, img in enumerate(uploaded_images):
                ProductImage.objects.create(
                    product=instance,
                    image=img,
                    is_primary=(not has_primary and idx == 0),
                    order=start_order + idx
                )
                if idx == 0:
                    has_primary = True

        remaining_images = instance.images.all()
        if remaining_images.exists() and not remaining_images.filter(is_primary=True).exists():
            first_img = remaining_images.first()
            first_img.is_primary = True
            first_img.save()

        return instance

class ProductOutputSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'seller',
            'category',
            'category_name',
            'name',
            'details',
            'price',
            'stock',
            'images',
            'average_rating',
            'created_at',
            'updated_at'
        ]

    def get_average_rating(self, obj):
        try:
            from reviews.models import Review
            from django.db.models import Avg
            result = Review.objects.filter(product=obj).aggregate(Avg('rating'))
            avg = result.get('rating__avg')
            return round(avg, 2) if avg is not None else 0.0
        except Exception:
            return 0.0

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'stock',
            'category_name',
            'primary_image',
            'average_rating'
        ]

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if not primary:
            primary = obj.images.first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None

    def get_average_rating(self, obj):
        try:
            from reviews.models import Review
            from django.db.models import Avg
            result = Review.objects.filter(product=obj).aggregate(Avg('rating'))
            avg = result.get('rating__avg')
            return round(avg, 2) if avg is not None else 0.0
        except Exception:
            return 0.0

class ProductDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']
