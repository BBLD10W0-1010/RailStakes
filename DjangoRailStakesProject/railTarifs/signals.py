from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserQuota

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_quota(sender, instance, created, **kwargs):
    if created:
        UserQuota.objects.create(user=instance, total_limit=5)