from django.shortcuts import render
from rest_framework import serializers
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from .permissions import IsVerified
from .viewsets import BaseCreateListRetrieveUpdateViewSet
from .twilio_sms import send_sms_msg

class RegisterView(APIView):

    def post(self, request):
        
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse(serializer.data)

# Use dryve go Viewset approach but for separate classes, we will have a base viewset aith auth and all
class PhoneNumberVerificationView(BaseCreateListRetrieveUpdateViewSet):

    def send_otp_sms(self, request, format=None, **kwargs):

        totp = pyotp.TOTP(request.user.key, interval=100)
        otp = totp.now()

        message = f"Your easebox confirmation code is {str(otp)}. Valid for 10 minutes, one-time use only."
        sent = send_sms_msg(message, request.user.phone_number)

        if sent:
            return Response(status=200)
        
        return Response(status=401)


    def verify_otp(self, request, format=None, **kwargs):

        user = request.user

        otp = int(request.data.get("sms_code"))

        if user.authenticate(otp):

            user.is_verified = True
            user.save()

            return Response(status=201)
        
        return Response(dict(detail="The provided code did not match or has expired"))
