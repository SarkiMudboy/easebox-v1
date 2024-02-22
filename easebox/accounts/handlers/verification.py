from django.contrib.auth.models import AbstractBaseUser
from .abstract import Handler
from typing import Dict, Optional, Any, List
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from ..verification.email.verify_email import verify_email, confirm_email
from ..verification.phone.passwords.otp import OTP
from ..tasks import send_verification_mail

from django.utils.encoding import force_str
from django.utils.http import  urlsafe_base64_decode

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
            self.clean_up(data)
            
            return error
            
    def verify(self, data: Dict[str, Any]) -> None:

        request = data.pop("request")
        user = data.pop("user")

        verify_email(request, user)

    @staticmethod
    def confirm_email(uid: str, token: str) -> bool:

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except (OverflowError, TypeError, ValueError, User.DoesNotExist):
            return False
        
        try:
            Verified(email=user.email)
        except ValidationError as e:
            return False
        
        return confirm_email(user, token)

    def clean_up(self, data: Dict[str, Any]) -> Dict[str, Any]:
    
        data.pop("request")
        data.pop("user")
    
        return data

    def response(self, data: Dict[str, Any]):
        return None


class PhoneNumberVerificationHandler(Handler):
    
    def run(self, data: Dict[str, Any], **kwargs):

        phone = self.transform(data, **kwargs)

        if not phone:
            return True

        errors = self.validate(phone)

        if errors:
            return errors

        self.verify(phone)

        return self.response()
    
    def transform(self, data: Dict[str, Any], **kwargs) -> str:
        user = None
        # remove request if its from sign iup
        if data.get("request"):
            data.pop("request")

        request = kwargs.get("request")
        if request:
            user = request.user
        else:
            user_id = data.get("id")

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return None

        return user.phone_number
    
    def validate(self, phone_number: str) -> Dict[str, str]:
        
        try:
            Verified(phone_number=phone_number)
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
            Verified(phone_number=phone_number)
        except ValidationError as e:
            return False

        provided_otp = 0
        try:
            provided_otp = str(otp)
        except:
            return False
        
        return OTP.verify_otp(provided_otp, phone_number, 200)

    def response(self):
        return None