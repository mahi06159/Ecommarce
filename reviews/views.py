from rest_framework import generics, status
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from reviews.permissions import IsBuyerOrReadOnly, IsReviewOwnerOrReadOnly
from ecom_project.utils import success_response, error_response

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET: List reviews (filter by 'product' or 'buyer' via query params).
    POST: Create a review (Buyer only).
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsBuyerOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all().select_related('buyer', 'product').order_by('-created_at')
        product_id = self.request.query_params.get('product')
        buyer_id = self.request.query_params.get('buyer')

        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if buyer_id:
            queryset = queryset.filter(buyer_id=buyer_id)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Instantiate ReviewSerializer directly to serialize a list of review objects
        # We pass request context for any request-dependent fields/methods
        serializer = ReviewSerializer(queryset, many=True, context={'request': request})
        return success_response(
            message="Reviews retrieved successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        # Instantiate ReviewSerializer directly to validate and submit a new review
        # We pass request context for downstream serializer check/save logic
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # Set the logged-in buyer as the author of this review
        serializer.save(buyer=request.user)
        return success_response(
            message="Review submitted successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve review details.
    PUT/PATCH: Update review details (Buyer owner of the review only).
    DELETE: Delete review (Buyer owner of the review only).
    """
    queryset = Review.objects.all().select_related('buyer', 'product')
    serializer_class = ReviewSerializer
    permission_classes = [IsBuyerOrReadOnly, IsReviewOwnerOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Review.objects.select_related('buyer', 'product').get(pk=kwargs['pk'])
        except Review.DoesNotExist:
            return error_response(
                message="Review not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        # Instantiate ReviewSerializer directly to serialize a single review object
        # We pass request context for downstream serializer logic
        serializer = ReviewSerializer(instance, context={'request': request})
        return success_response(
            message="Review details retrieved.",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = Review.objects.select_related('buyer', 'product').get(pk=kwargs['pk'])
        except Review.DoesNotExist:
            return error_response(
                message="Review not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        # Instantiate ReviewSerializer directly to update the review details
        # We pass request context for downstream serializer validation or saving logic
        serializer = ReviewSerializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            message="Review updated successfully.",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = Review.objects.select_related('buyer', 'product').get(pk=kwargs['pk'])
        except Review.DoesNotExist:
            return error_response(
                message="Review not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return success_response(
            message="Review deleted successfully."
        )
