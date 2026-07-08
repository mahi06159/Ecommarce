from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from authentication.models import BuyerProfile, SellerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'Buyer':
            BuyerProfile.objects.get_or_create(user=instance)
        elif instance.role == 'Seller':
            SellerProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'Buyer':
        if hasattr(instance, 'buyer_profile'):
            instance.buyer_profile.save()
    elif instance.role == 'Seller':
        if hasattr(instance, 'seller_profile'):
            instance.seller_profile.save()
