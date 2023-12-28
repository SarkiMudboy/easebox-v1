from django.urls import path
from .views import RegisterView, PhoneNumberVerificationView, EmailVerificationView, EmailConfirmationView, LoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

send_otp = PhoneNumberVerificationView.as_view({"get": "send_otp_sms"})
verify_phone_otp = PhoneNumberVerificationView.as_view({"post": "verify_otp"})

confirm_email = EmailConfirmationView.as_view({"get": "confirm_email_token"})
verify_email = EmailVerificationView.as_view({"post": "verify_email"})

urlpatterns = [
    path('register-user/', RegisterView.as_view(), name="sign-up"),

    # jwt
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # email
    path('verify-email/', verify_email, name="email-verify"),
    path('verify-email-confirm/<uid>/<token>/', confirm_email, name="verify-email-confirm"),

    # phone
    path("send-phone-otp/", send_otp, name='send-phone-otp'),
    path("verify-phone-otp/", verify_phone_otp, name='verify-phone-otp'),
]
