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

# from six import text_type
import pendulum

User: AbstractBaseUser = get_user_model()

class PasswordRecoveryHandlerFactory(object):

    @staticmethod
    def get(endpoint: str) -> Handler:

        endpoint_handlers = {
            "email": EmailPasswordRecoveryHandler,
            # "phone": PhonePasswordRecoveryHandler
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
        if user.is_superuser:
            return data, {"user": "Unauthorized resource"}
        
        return data, None # for now
    
    def send_recovery_email(self, data: Dict[str, Any], **kwargs) -> None:
        # this would have the flow from verify_email.py
        # we need user, request scheme, request current site

        user: AbstractBaseUser = data.get("user")
        email_token = PasswordResetTokenGenerator()
        password_reset_token = email_token.make_token(user)

        user.password_reset_key = password_reset_token
        user.password_reset_key_expires = pendulum.now("UTC").add(days=7)

        user_id = urlsafe_base64_encode(force_bytes(user.id))
        recovery_url = self._generate_recovery_url(user_id, password_reset_token, **kwargs)

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
    
    def _generate_recovery_url(self, user_id: str, token:str, **kwargs) -> str:

        domain, scheme = self._get_request_data(kwargs.get("request"))
        password_recovery_path: str = reverse("accounts:verify-reset-password", kwargs={"uid": user_id, "token": token})
        url: str = "%s://%s%s"%(scheme, domain, password_recovery_path)
        return url
    
    @staticmethod
    def verify(uid: str, token: str) -> bool:
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except (OverflowError, TypeError, ValueError, User.DoesNotExist):
            return False
        
        email_token = PasswordResetTokenGenerator()
        if user is not None and email_token.check_token(user, token) and user.password_reset_key_expires > pendulum.now():
            return True
        return False
    
    def response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data, None