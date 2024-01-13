from django.contrib.auth.models import AbstractBaseUser
from .abstract import Handler
from typing import Dict, Optional, Any, List
from django.contrib.auth import get_user_model
from ..verification.email.verify_email import verify_email, confirm_email
from ..verification.phone.passwords.otp import OTP
from ..tasks import send_verification_mail

from ..validation.models import Verified
from ..validation.validators import handle_errors
from pydantic import ValidationError

User = get_user_model()

class VerificationHandlerFactory(object):

    @staticmethod
    def get(endpoint: str) -> Handler:

        enpoint_handlers = {
            "email": EmailVerificationHandler,
            "phone": PhoneNumberVerificationHandler,
        }

        return enpoint_handlers[endpoint]()
    


class EmailVerificationHandler(Handler):
    
    def run(self, data, *kwargs):

        data = self.transform(data)

        error = self.validate(data)

        if error:
            return error
        
        self.verify(data)

        return self.response(data)
    
    def transform(self, data: Dict[str, Any]) -> dict:

        if not data.get("id"):
            data["user"] = data.get("request").user
        else:
            data["user"] = User.objects.get(id=data.get("id"))

        return data 
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:

        user = data.get("user")

        try:
            Verified(email=user.email)
        except ValidationError as e:

            error = handle_errors(e.errors())

            return error
            
    def verify(self, data: Dict[str, Any]) -> None:

        request = data.pop("request")
        user = data.get("user")

        verify_email(request, user)

    @staticmethod
    def confirm_email(user: AbstractBaseUser ,uid: str, token: str) -> bool:

        try:
            Verified(phone=user.phone_number)
        except ValidationError as e:
            return False
        
        return confirm_email(uid, token)

    def response(self, data: Dict[str, Any]):
        return None


class PhoneNumberVerificationHandler(Handler):
    
    def run(self, data: Dict[str, Any], *kwargs):

        phone = self.transform(data)

        if not phone:
            return True

        errors = self.validate(phone)

        if errors:
            return errors

        self.verify(phone)

        return self.response()
    
    def transform(self, data: Dict[str, Any]) -> str:

        if data.get("request"):
            data.pop("request")

        user_id = data.get("id")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

        return user.phone_number
    
    def validate(self, phone_number: str) -> Dict[str, str]:
        
        try:
            Verified(phone=phone_number)
        except ValidationError as e:
            error = handle_errors(e.errors)

            return error

    def verify(self, phone_number: str) -> None:

        interval = 200
        otp = OTP.generate_otp(phone_number, interval)

        email = "ihimaabdool@gmail.com"
        subject = "Confirm phone number"

        sms_message = f"Your easebox confirmation code is {str(otp)}. Valid for 10 minutes, one-time use only."

        send_verification_mail.delay(subject, sms_message, email)

    def authenticate(self, otp, phone_number) -> bool:

        "This authenticates the given otp for phone number verification"

        try:
            Verified(phone=phone_number)
        except ValidationError:
            return False

        provided_otp = 0
        try:
            provided_otp = str(otp)
        except:
            return False
        
        return OTP.verify_otp(provided_otp, phone_number, 200)

    def response(self):
        return None