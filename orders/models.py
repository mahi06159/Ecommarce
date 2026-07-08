from django.db import models
from django.conf import settings
from products.models import Product
from ecom_project.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin
from simple_history.models import HistoricalRecords
import uuid

class Address(TimestampMixin, SoftDeleteMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.extend([self.city, self.state, self.postal_code, self.country])
        return ", ".join(parts)


class Order(TimestampMixin, SoftDeleteMixin, AuditMixin):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    shipping_address_text = models.TextField(default="", blank=True, help_text="Snapshot of address details at checkout")

    history = HistoricalRecords()

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username} - {self.status}"


class OrderItem(TimestampMixin, SoftDeleteMixin):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    product_name = models.CharField(max_length=255, default="", blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of product at time of order placement")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')

    history = HistoricalRecords()

    def __str__(self):
        name = self.product.name if self.product else self.product_name
        return f"OrderItem #{self.id} (Order #{self.order.id}): {name} x {self.quantity}"


class Cart(TimestampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )

    def __str__(self):
        return f"Cart {self.id} (User: {self.user.username if self.user else 'Anonymous'})"


class CartItem(TimestampMixin):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Cart {self.cart.id}"


class Payment(TimestampMixin):
    STATUS_CHOICES = (
        ('Created', 'Created'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Created')

    def __str__(self):
        return f"Payment {self.razorpay_order_id} - Order {self.order_id if self.order else 'Pending'} - {self.status}"





