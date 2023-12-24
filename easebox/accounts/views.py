import re
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from rest_framework import serializers
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer
from rest_framework.response import Response
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from rest_framework import status

# from .permissions import IsVerified
from .viewsets import AuthViewSet
# from abstract.services.sms.twilio_sms import send_sms_msg
from .verification.email.verify_email import verify_email, confirm_email
from .handlers.users import AccountHandlerFactory
from .handlers.verification import VerificationHandlerFactory
# import pyotp


class RegisterView(APIView):

    def post(self, request):
        
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save() remove this 

        print(serializer.data)

        handler = AccountHandlerFactory.get("create-business-user")
        response = handler.run(serializer.data, request=request)

        id_field = "email" if not serializer.data.get("phone_number") else "phone_number"
        user = authenticate(request, username=serializer.data[id_field], password=request.data["password"])

        if user:
            return JsonResponse(response, status=status.HTTP_201_CREATED)
        
        return Response(400)


class EmailVerificationView(AuthViewSet):

    def verify_email(self, request):

        data = request.data
        data["request"] = request

        handler = VerificationHandlerFactory.get("email")
        handler.run(data)

class EmailConfirmationView(AuthViewSet):

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def confirm_email_token(self, request, uid, token):

        verified = confirm_email(uid, token)

        if verified:
            return Response(200)
        
        return Response(400)


class PhoneNumberVerificationView(AuthViewSet):

    def send_otp_sms(self, request, format=None, **kwargs):

        user = request.user

        handler = VerificationHandlerFactory.get("phone")
        error = handler.run(user.phone_number)

        if error:

            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    def verify_otp(self, request, format=None, **kwargs):

        user = request.user

        otp = int(request.data.get("sms_code"))

        handler = VerificationHandlerFactory.get("phone")

        if handler.auhtenticate(otp):

            user.is_verified = True
            user.save()

            return Response({"email": "Your email has been verified"}, status=status.HTTP_200_OK)
        
        return Response(dict(error="The provided code did not match or has expired"), status=status.HTTP_401_BAD_REQUEST)
