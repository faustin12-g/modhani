from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProductInteraction, Cart, OrderItem

@receiver(post_save, sender=Cart)
def track_cart_additions(sender, instance, created, **kwargs):
    if created and instance.user:
        UserProductInteraction.objects.update_or_create(
            user=instance.user,
            product=instance.product,
            interaction_type='add_to_cart',
            defaults={'interaction_weight': 0.5}
        )

@receiver(post_save, sender=OrderItem)
def track_purchases(sender, instance, created, **kwargs):
    if created and instance.order.user:
        UserProductInteraction.objects.update_or_create(
            user=instance.order.user,
            product=instance.product,
            interaction_type='purchase',
            defaults={'interaction_weight': 1.0}
        )
