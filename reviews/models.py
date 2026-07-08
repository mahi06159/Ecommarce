from django.db import models
from django.conf import settings
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from ecom_project.mixins import TimestampMixin, SoftDeleteMixin
from simple_history.models import HistoricalRecords

class Review(TimestampMixin, SoftDeleteMixin):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()

    history = HistoricalRecords()

    class Meta:
        # Enforce that a single buyer can only review a product once.
        unique_together = ('buyer', 'product')

    def __str__(self):
        return f"Review by {self.buyer.username} on {self.product.name} - Rating: {self.rating}"


