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

        cls.key = hotp(k, time_steps)

        return cls

    @classmethod
    def verify(cls, otp: int) -> bool:
        
        if cls.key == otp:
            return True
        return False

class OTP:
    '''Class for generating and verifying OTPs (Time-based)'''

    @classmethod
    def generate_key(cls, phone_number: str) -> str:

        key = str(phone_number)
        return base64.b32encode(key.encode())

    def generate_otp(cls, phone_number: str, interval: int) -> int:

        "Generates phone number verification OTP for user"
        key = cls.generate_key(phone_number)
        OTP = HOTP().totp(key, interval)
        print(OTP.key)

        try:
            User.objects.get(phone_number_verification_key=OTP.key)
        except User.DoesNotExist:
            return OTP.key
        
        cls.generate_otp(phone_number)

    @classmethod
    def verify_otp(cls, otp: int, phone: str, interval: int) -> bool:
        
        key = cls.generate_key(phone)
        OTP = HOTP().totp(key, interval)
        print(OTP.key)
        if OTP.verify(otp):
            return OTP.key
        return False