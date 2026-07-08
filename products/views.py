from rest_framework import generics, status
from products.models import Category, Product
from products.serializers import (
    CategorySerializer,
    ProductInputSerializer,
    ProductOutputSerializer,
    ProductListSerializer,
    ProductDropdownSerializer
)
from products.permissions import IsSellerOrReadOnly
from ecom_project.utils import success_response, error_response

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories.
    POST: Create a new category (Seller only).
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsSellerOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Instantiate CategorySerializer directly to serialize the list of category objects
        serializer = CategorySerializer(queryset, many=True)
        return success_response(
            message="Categories retrieved successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        # Instantiate CategorySerializer directly to validate and deserialize the input data
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            message="Category created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve category details.
    PUT/PATCH: Update category details (Seller only).
    DELETE: Delete category (Seller only).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSellerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Category.objects.get(pk=kwargs['pk'])
        except Category.DoesNotExist:
            return error_response(
                message="Category not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        # Instantiate CategorySerializer directly to serialize a single category object
        serializer = CategorySerializer(instance)
        return success_response(
            message="Category details retrieved.",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = Category.objects.get(pk=kwargs['pk'])
        except Category.DoesNotExist:
            return error_response(
                message="Category not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        # Instantiate CategorySerializer directly to update and validate category data
        serializer = CategorySerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            message="Category updated successfully.",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Category.objects.get(pk=kwargs['pk'])
        except Category.DoesNotExist:
            return error_response(
                message="Category not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return success_response(
            message="Category deleted successfully."
        )

class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET: List all products. Support filtering by category & seller, search by name.
    POST: Create a product (Seller only).
    """
    serializer_class = ProductListSerializer
    permission_classes = [IsSellerOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.select_related('seller', 'category').order_by('-created_at')
        
        # Simple manual filtering
        category_id = self.request.query_params.get('category')
        seller_id = self.request.query_params.get('seller')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
            
        # Simple search on product name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return success_response(
            message="Products retrieved successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = ProductInputSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save(seller=self.request.user)
        output_serializer = ProductOutputSerializer(product, context={'request': request})
        return success_response(
            message="Product created successfully.",
            data=output_serializer.data,
            status_code=status.HTTP_201_CREATED
        )

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve product details.
    PUT/PATCH: Update product details (Seller owner only).
    DELETE: Delete product (Seller owner only).
    """
    queryset = Product.objects.all().select_related('seller', 'category')
    serializer_class = ProductOutputSerializer
    permission_classes = [IsSellerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Product.objects.select_related('seller', 'category').get(pk=kwargs['pk'])
        except Product.DoesNotExist:
            return error_response(
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        serializer = ProductOutputSerializer(instance, context={'request': request})
        return success_response(
            message="Product details retrieved.",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = Product.objects.select_related('seller', 'category').get(pk=kwargs['pk'])
        except Product.DoesNotExist:
            return error_response(
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        serializer = ProductInputSerializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        output_serializer = ProductOutputSerializer(product, context={'request': request})
        return success_response(
            message="Product updated successfully.",
            data=output_serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Product.objects.select_related('seller', 'category').get(pk=kwargs['pk'])
        except Product.DoesNotExist:
            return error_response(
                message="Product not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return success_response(
            message="Product deleted successfully."
        )

    def perform_destroy(self, instance):
        instance.delete()

class ProductDropdownListView(generics.ListAPIView):
    """
    GET: List all products (minimal detail: id, name) for dropdowns.
    """
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductDropdownSerializer
    permission_classes = [IsSellerOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProductDropdownSerializer(queryset, many=True)
        return success_response(
            message="Product dropdown list retrieved successfully.",
            data=serializer.data
        )
