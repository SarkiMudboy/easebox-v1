import base64
import pyotp
import time
from datetime import datetime
from django.contrib.auth import get_user_model
from .totp import hotp

User = get_user_model()


class HOTP:

    @classmethod
    def totp(cls, k, t):

        s_since_epoch = time.mktime(datetime.now().timetuple())
        time_steps = int(s_since_epoch/t)

        key = hotp(k, time_steps)
        cls.key = str(key)

        return cls

    @classmethod
    def verify(cls, otp: str) -> bool:
        
        if cls.key == otp:
            return True
        return False


def generate_key(phone_number: str) -> str:

    key = str(phone_number)
    return base64.b32encode(key.encode())


class OTP:
    '''Class for generating and verifying OTPs (Time-based)'''

    @staticmethod
    def generate_otp(phone_number: str, interval: int) -> str:

        "Generates phone number verification OTP for user"
        key = generate_key(phone_number)
        password = HOTP().totp(key, interval)

        try:
            User.objects.get(phone_number_verification_key=password.key)
        except User.DoesNotExist:
            return str(password.key)
        
        OTP.generate_otp(phone_number)

    @staticmethod
    def verify_otp(otp: str, phone: str, interval: int) -> bool:
        
        key = generate_key(phone)
        OTP = HOTP().totp(key, interval)
        
        return OTP.verify(otp)