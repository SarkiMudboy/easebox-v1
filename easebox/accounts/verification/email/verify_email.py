from multiprocessing.context import _force_start_method
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import AbstractBaseUser
from django.contrib import messages
from django.urls import reverse

from ...tasks import send_verification_mail

from .email_activation_token import email_verification_token
import pendulum


User: AbstractBaseUser = get_user_model()


def verify_email(request, user: AbstractBaseUser) -> bool:

    url = get_current_site(request)
    user_id = urlsafe_base64_encode(force_bytes(user.id))
    verification_token = email_verification_token.make_token(user)

    user.email_verification_key = verification_token
    user.email_verification_key_expires = pendulum.now("UTC").add(days=7)
    user.save()

    verify_email_path = reverse("verify-email-confirm", kwargs={"uid": user_id, "token": verification_token})

    email = user.email
    subject = "Verify Email"
    verification_url = "%s://%s%s"%(request.scheme, url.domain, verify_email_path)
    
    context = {
        "request": request,
        "user": user,
        "verification_url": verification_url,
    }

    message = render_to_string("accounts/verify-email.html", context)

    send_verification_mail.delay(subject, message, email)


def confirm_email(uid: str, token: str) -> bool:

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=user_id)
    except (OverflowError, TypeError, ValueError, User.DoesNotExist):
        user = None
    
    if user is not None and not user.is_email_verified and email_verification_token.check_token(user, token) and user.email_verification_key_expires > pendulum.now():

        user.is_email_verified = True
        user.save()

        return True
    
    return False
