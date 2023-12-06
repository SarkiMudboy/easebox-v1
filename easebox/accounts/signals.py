from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserAccount
import pyotp


def generate_key() -> int:

    "Generates phone number verification OTP for user"
    key = pyotp.TOTP('base32secret3232')

    try:
        User.objects.get(phone_number_verification_key=key)
    except User.DoesNotExist:
        return key
    
    generate_key()


@receiver(pre_save, sender=User)
def create_phone_verification_key(sender: User, instance: User, **kwargs) -> None:
    if instance.phone_number:
        if not instance.phone_number_verification_key:
            instance.phone_number_verification_key = generate_key()


@receiver(post_save, sender=User)
def create_user_account(sender: User, instance: User, created: bool, **kwargs) -> None:
    if created:
        UserAccount.objects.create(owner=instance)