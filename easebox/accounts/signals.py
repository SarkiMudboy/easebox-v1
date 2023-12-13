from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserAccount
# from .verification.phone.verify_phone import OTP
# import pyotp

# @receiver(pre_save, sender=User)
# def create_phone_verification_key(sender: User, instance: User, **kwargs) -> None:
#     if instance.phone_number:
#         if not instance.phone_number_verification_key:
#             instance.phone_number_verification_key = OTP.generate_otp(instance.phone_number)


@receiver(post_save, sender=User)
def create_user_account(sender: User, instance: User, created: bool, **kwargs) -> None:
    if created:
        UserAccount.objects.create(owner=instance)