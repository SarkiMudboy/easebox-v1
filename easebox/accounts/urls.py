from django.urls import path
from .views import RegisterView, PhoneNumberVerificationView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

send_otp = PhoneNumberVerificationView.as_view({"get": "send_otp_sms"})
verify_phone_otp = PhoneNumberVerificationView.as_view({"post": "verify_otp"})

urlpatterns = [
    path('register-user/', RegisterView.as_view(), name="sign-up"),

    # jwt
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("send-phone-otp/", send_otp, name='send-phone-otp'),
    path("verify-phone-otp/", verify_phone_otp, name='verify-phone-otp'),
]
