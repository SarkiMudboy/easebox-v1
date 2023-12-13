from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class EmailTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        
        return text_type(user.pk) + text_type(timestamp) + text_type(user.is_email_verified)
    
email_verification_token = EmailTokenGenerator()