from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.conf import settings
from ecom_project.mixins import TimestampMixin, SoftDeleteMixin

class SoftDeleteUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

class User(AbstractUser, SoftDeleteMixin, TimestampMixin):
    ROLE_CHOICES = (
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Buyer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    objects = SoftDeleteUserManager()

    REQUIRED_FIELDS = ['email', 'role']

    def __str__(self):
        return f"{self.username} ({self.role})"

    def delete(self, *args, **kwargs):
        if hasattr(self, 'buyer_profile'):
            self.buyer_profile.delete()
        if hasattr(self, 'seller_profile'):
            self.seller_profile.delete()
        self.is_deleted = True
        self.is_active = False
        import time
        timestamp = int(time.time())
        original_username = self.username
        original_email = self.email
        self.username = f"{original_username}_deleted_{timestamp}"[:150]
        if original_email:
            if '@' in original_email:
                local, domain = original_email.split('@', 1)
                self.email = f"{local}_deleted_{timestamp}@{domain}"[:254]
            else:
                self.email = f"{original_email}_deleted_{timestamp}"[:254]
        self.save(*args, **kwargs)
        return (1, {self._meta.label: 1})

class BuyerProfile(SoftDeleteMixin, TimestampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_profile'
    )
    avatar = models.ImageField(upload_to='buyer_avatars/', blank=True, null=True)

    def __str__(self):
        return f"Buyer Profile: {self.user.username}"


class SellerProfile(SoftDeleteMixin, TimestampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    store_name = models.CharField(max_length=255, blank=True, null=True)
    store_description = models.TextField(blank=True, null=True)
    store_logo = models.ImageField(upload_to='seller_logos/', blank=True, null=True)

    def __str__(self):
        return f"Seller Profile: {self.user.username}"




