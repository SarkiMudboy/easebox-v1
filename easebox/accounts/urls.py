from django.urls import path
from .views import (
    RegisterBusinessUserView, PhoneNumberVerificationView, 
    EmailVerificationView, EmailConfirmationView, 
    LoginView, PasswordRecoveryView,
    )
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'accounts'

send_otp = PhoneNumberVerificationView.as_view({"get": "send_otp_sms"})
verify_phone_otp = PhoneNumberVerificationView.as_view({"post": "verify_otp"})

confirm_email = EmailConfirmationView.as_view({"get": "confirm_email_token"})
verify_email = EmailVerificationView.as_view({"post": "verify_email"})

forgot_password = PasswordRecoveryView.as_view({"get": "forgot_password"})
verify_reset_password = PasswordRecoveryView.as_view({"get": "verify_reset_password"})

urlpatterns = [
    path('register-business-user/', RegisterBusinessUserView.as_view(), name="business-user-sign-up"),

    # jwt
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # email
    path('verify-email/', verify_email, name="email-verify"),
    path('confirm-email/<uid>/<token>/', confirm_email, name="confirm-email"),

    # phone
    path("send-phone-otp/", send_otp, name='send-phone-otp'),
    path("verify-phone-otp/", verify_phone_otp, name='verify-phone-otp'),

    # password
    path("forgot-password/", forgot_password, name="forgot-password"),
    path("verify-reset-password/<uid>/<token>/", forgot_password, name="verify-reset-password"),
]
