from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from typing import Any, Dict, Optional, Tuple
from .abstract import Handler
from ..tasks import send_password_recovery_mail
from ..verification.phone.passwords.otp import OTP

from six import text_type
import pendulum
import secrets
import hashlib

User: AbstractBaseUser = get_user_model()

class PasswordRecoveryHandlerFactory(object):

    @staticmethod
    def get(endpoint: str) -> Handler:

        endpoint_handlers = {
            "email": EmailPasswordRecoveryHandler,
            "phone": PhonePasswordRecoveryHandler
        }

        return endpoint_handlers[endpoint]()


class EmailPasswordRecoveryHandler(Handler):

    def run(self, data: Dict[str, Any], **kwargs)-> Dict[str, Any]:

        data = self.transform(data) # do nun
        data, errors = self.validate(data) # check that the account is not suspended...

        if errors:
            return data, errors
        
        self.send_recovery_email(data, **kwargs)
        return self.response(data)
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:

        email = data.get("email")
        user = User.objects.get(email=email)
        data["user"] = user
        return data
    
    def validate(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], None]:

        user = data.get("user")
        # check that it's not a superuser
        if user.is_superuser:
            return data, {"user": "Unauthorized resource"}
        
        return data, None # for now
    
    def send_recovery_email(self, data: Dict[str, Any], **kwargs) -> None:

        user: AbstractBaseUser = data.get("user")
        user_id = urlsafe_base64_encode(force_bytes(user.id))
        email_recovery_url = reverse("accounts:verify-reset-password", kwargs={"uid": user_id})

        user.active_password_reset_link = True
        user.password_reset_key_expires = pendulum.now("UTC").add(minutes=5)
        user.save()

        recovery_url = self._generate_recovery_url(email_recovery_url, **kwargs)
        context = {
            "request": kwargs.get("request"),
            "user": user,
            "recovery_url": recovery_url,
        }
        email: str = user.email
        subject: str = "Recover Password"
        message: str = render_to_string("accounts/recover-password.html", context)
        send_password_recovery_mail.delay(subject, message, email)

    def _get_request_data(self, request: HttpRequest) -> Tuple[str]:
        url: RequestSite = get_current_site(request)
        return url.domain, request.scheme
    
    def _generate_recovery_url(self, url_path: str, **kwargs) -> str:
        domain, scheme = self._get_request_data(kwargs.get("request")) 
        url: str = "%s://%s%s"%(scheme, domain, url_path)
        return url
    
    def generate_token(self, uid: str) -> Tuple[Dict[str, str], bool]:
        
        try:
            user_id: str = force_str(urlsafe_base64_decode(uid))
            user: AbstractBaseUser = User.objects.get(id=user_id)
        except (OverflowError, TypeError, ValueError, User.DoesNotExist):
            return None, True
        
        # check to see if the link has been redeemed/key has not expired
        if not user.active_password_reset_link or user.password_reset_key_expires < pendulum.now():
            return None, True
        user.active_password_reset_link = False
        # generate a token using secrets.urlsafe
        password_token = secrets.token_urlsafe(50)
        # hash it
        token_hash = hashlib.sha256(password_token.encode("utf-8")).hexdigest()
        # assign to user.password_reset_key
        user.password_reset_key = token_hash
        # user.password_reset_key_expires = pendulum.now("UTC").add(minutes=5)
        user.save()

        # generate the url using reverse and the genrate_recovery_url method
        url_path = reverse("accounts:reset-password", kwargs={"token": password_token})
        # return the url in a response dict to be used by the template
        context_data = {
            "reset_password_url": url_path
            }
        return context_data, False
    
    def verify(self, token: str) -> AbstractBaseUser:
        # get the token
        # hash it 
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        # compare with hashed value in the db (query which user has an identical hash) AND check the expiry
        try:
            user = User.objects.get(password_reset_key=token_hash)
        except (OverflowError, TypeError, ValueError, User.DoesNotExist):
            return None
         
        if user.password_reset_key_expires < pendulum.now():
            return None
        
        # delete the value form db
        user.password_reset_key = None
        user.save()
        return user

    def reset_password(self, data: Dict[str, Any], token: str) -> Tuple[Dict[str, str], bool]:
        user = self.verify(token)
        if not user:
            return None, True
        
        password = data.get("password")
        user.set_password(password)
        user.save()
        return {}, False

    def response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data, None
    
class PhonePasswordRecoveryHandler(Handler):

    def run(self, data: Dict[str, Any], **kwargs) -> Tuple[Dict[str, Any], bool]:
        data = self.transform(data)
        data, error = self.validate(data)
        if error:
            return None, True
        
        self.send_recovery_otp(data)
        return self.response(data)
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        phone = data.get("phone_number")
        user = User.objects.get(phone_number=phone)
        data["user"] = user

        return data
    
    def validate(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        user = data.get("user")
        # check that it's not a superuser
        if user.is_superuser:
            return data, {"user": "Unauthorized resource"}
        
        return data, None # for now
    
    def send_recovery_otp(self, data: Dict[str, Any]) -> None:
        user = data["user"]
        interval = 200
        otp = OTP.generate_otp(user.phone_number, interval)

        user.password_reset_otp = otp
        user.password_reset_key_expires = pendulum.now("UTC").add(minutes=5) # change the time here, can't have it being less than the otp
        user.save()

        email = "ihimaabdool@gmail.com"
        subject = "Reset Password"
        sms_message = f"Your password reset OTP code is {str(otp)}. Valid for 10 minutes, one-time use only."

        send_password_recovery_mail.delay(subject, sms_message, email)

    def verify_otp(self, otp: str) -> Optional[str]:
        # get the user
        try:
            user = User.objects.get(password_reset_otp=otp)
        except (OverflowError, ValueError, User.DoesNotExist):
            return None
        else:
            user.password_reset_otp = None
        
        provided_otp = 0
        try:
            provided_otp = str(otp)
        except:
            return None
        
        if OTP.verify_otp(provided_otp, user.phone_number, 200) and user.password_reset_key_expires > pendulum.now():

            # generate a token using secrets.urlsafe
            password_token = secrets.token_urlsafe(50)
            # hash it
            token_hash = hashlib.sha256(password_token.encode("utf-8")).hexdigest()
            # assign to user.password_reset_key
            user.password_reset_key = token_hash
            # user.password_reset_key_expires = pendulum.now("UTC").add(minutes=5)
            user.save()

            return reverse("accounts:reset-password", kwargs={"token": password_token})
        
        return None
    
    def reset_password(self, data: Dict[str, Any], token:str) -> Tuple[Dict[str, str], bool]:

        token_hash = secrets.token_urlsafe(token)

        try:
            user = User.objects.get(password_reset_key=token_hash)
        except (OverflowError, ValueError, User.DoesNotExist):
            return None, False
        
        if user.password_reset_key_expires < pendulum.now():
            return None, False
        
        user.password_reset_key = None
        user.set_password(data.get("password"))
        user.save()

        return {}, True

    def response(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        return data, False

        
        