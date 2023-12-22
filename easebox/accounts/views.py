import re
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from rest_framework import serializers
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage
from rest_framework import status

from .permissions import IsVerified
from .viewsets import BaseCreateListRetrieveUpdateViewSet, AuthViewSet
from abstract.services.sms.twilio_sms import send_sms_msg
from .verification.email.verify_email import verify_email, confirm_email
import pyotp


class RegisterView(APIView):

    def post(self, request):
        
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save() remove this 

        print(serializer.data)

        id_field = "email" if not serializer.data.get("phone_number") else "phone_number" # move to verification handler

        #after class returns

        user = authenticate(request, username=serializer.data[id_field], password=request.data["password"])

        # create a verification class that verifies either phone or email*
        if user and id_field == "email":
            sent = verify_email(request, user)

        return JsonResponse(serializer.data)


class EmailVerificationView(AuthViewSet):

    def confirm_email_token(self, request, uid, token):

        verified = confirm_email(uid, token)

        if verified:
            return Response(200)
        
        return Response(400)


class PhoneNumberVerificationView(BaseCreateListRetrieveUpdateViewSet):

    def send_otp_sms(self, request, format=None, **kwargs):

        cotp = pyotp.HOTP(request.user.key)
        otp = cotp.at(1)

        sms_message = f"Your easebox confirmation code is {str(otp)}. Valid for 10 minutes, one-time use only."

        email = EmailMessage("Verify phone", sms_message, to=[request.user.email])
        
        try:
            email.send()
        except Exception as e:
            print(str(e))

            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

    def verify_otp(self, request, format=None, **kwargs):

        user = request.user

        otp = int(request.data.get("sms_code"))

        if user.authenticate(otp):

            user.is_verified = True
            user.save()

            return Response({"email": "Your email has been verified"}, status=status.HTTP_200_OK)
        
        return Response(dict(error="The provided code did not match or has expired"), status=status.HTTP_401_BAD_REQUEST)
