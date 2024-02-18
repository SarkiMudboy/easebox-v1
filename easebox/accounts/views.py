import re
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.shortcuts import render
from rest_framework import serializers
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .serializers import RegisterBusinessUserSerializer, LoginSerializer, PasswordRecoverySerializer
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth import authenticate
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets

# from .permissions import IsVerified
from .viewsets import AuthViewSet, AnonViewSet
from .verification.email.verify_email import verify_email, confirm_email
from .handlers.users import AccountHandlerFactory
from .handlers.verification import VerificationHandlerFactory
from .handlers.passwords import PasswordRecoveryHandlerFactory


User: AbstractBaseUser = get_user_model()

class RegisterBusinessUserView(GenericAPIView):

    serializer_class = RegisterBusinessUserSerializer
    queryset = User.objects.all()

    def post(self, request) -> Response:
        
        serializer = RegisterBusinessUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        handler = AccountHandlerFactory.get("create-business-user")
        response, errors = handler.run(serializer.data, request=request)
        
        if errors:
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)

        id_field = "email" if not serializer.data.get("phone_number") else "phone_number"
        user = authenticate(request, username=serializer.data[id_field], password=request.data["password"])

        if user:
            return JsonResponse(response, status=status.HTTP_201_CREATED)
        
        return Response(400)


class LoginView(APIView):

    def post(self, request: HttpRequest) -> Response:

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        id_field = "email" if not serializer.data.get("phone_number") else "phone_number"
        user = authenticate(request, username=data[id_field], password=data["password"])

        if not user or not user.is_active:
            return JsonResponse({"detail": "invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED) # change the message here
        
        refresh = RefreshToken.for_user(user)

        response = {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }

        return JsonResponse(response, status=status.HTTP_200_OK)



class EmailVerificationView(AuthViewSet):

    def verify_email(self, request: HttpRequest) -> Response:

        data = request.data
        data["request"] = request

        handler = VerificationHandlerFactory.get("email")
        errors = handler.run(data)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

class EmailConfirmationView(AuthViewSet):

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    renderer_classes = [TemplateHTMLRenderer]

    def confirm_email_token(self, request: HttpRequest, uid: str, token: str) -> Response:

        verified = VerificationHandlerFactory.get("email").confirm_email(uid, token)
        if verified:
            return Response({}, template_name="accounts/email-verified.html")
        
        return Response(400)


class PhoneNumberVerificationView(AuthViewSet):

    def send_otp_sms(self, request: HttpRequest, format=None, **kwargs) -> Response:

        user = request.user
        handler = VerificationHandlerFactory.get("phone")
        error = handler.run(user.phone_number)

        if error:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    def verify_otp(self, request: HttpRequest, format=None, **kwargs) -> Response:

        user = request.user
        otp = str(request.data.get("sms_code"))
        handler = VerificationHandlerFactory.get("phone")

        if handler.authenticate(otp, user.phone_number):

            user.is_phone_number_verified = True
            user.phone_number_verification_key = otp # I may be wrong to put it here I dunno
            user.save()

            return Response({"phone": "Your phone number has been verified"}, status=status.HTTP_200_OK)
        
        return Response(dict(error="The provided code did not match or has expired"), status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryView(AnonViewSet):

    def forgot_password(self, request: HttpRequest, format=None, **kwargs) -> Response:
        # print("action->", self.action)

        serializer = PasswordRecoverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        id_field = "email" if not serializer.data.get("phone_number") else "phone"
        # handle the recovery
        handler = PasswordRecoveryHandlerFactory.get(id_field)
        _, error = handler.run(data, request=request)

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse({"response": "success"}, status=status.HTTP_200_OK)

    def verify_reset_password(self, request: HttpRequest, uid: str, token: str) -> Response:

        print("verified -> ")
        verified = PasswordRecoveryHandlerFactory.get("email").verify(uid, token)
        if not verified:
            return Response(400)
        
        return Response({}, template_name="accounts/reset-password.html")
        
