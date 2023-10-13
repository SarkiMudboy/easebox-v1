from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserAccount

@receiver(post_save, sender=User)
def create_user_account(sender: User, instance: User, created: bool, **kwargs) -> None:
    if created:
        UserAccount.objects.create(owner=instance)