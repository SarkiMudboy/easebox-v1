from xml.dom import ValidationErr
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password

from .models import User
from .twilio_sms import send_sms_msg
import pyotp


class RegisterUserSerializer(serializers.ModelSerializer):

    # remove these fields from the serialized response if they're null
    null_fields = ["email", "phone_number"]

    phone_number = serializers.CharField(
        required=False,
		validators=[UniqueValidator(queryset=User.objects.all())]
    )

    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    tokens = serializers.SerializerMethodField()

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "phone_number", "first_name", "last_name", "password", "password2", "tokens"]
        extra_kwargs = {"password": {"write_only": True}, "password2": {"write_only": True}}

    def validate(self, attrs):

        if attrs.get('password2'):
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({'password': 'Passwords must match.'})
        else:
            raise serializers.ValidationError("Confirm password")
            
        if not attrs.get("email") and not attrs.get("phone_number"):
            raise serializers.ValidationError("Email or phone number must be provided.")
        
        if not attrs.get("first_name") or not attrs.get("last_name"):
            raise serializers.ValidationError("First name and Last name must be provided.")

        return attrs

    
    def create(self, validated_data):
        
        validated_data.pop("password2")
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        # send verification sms
        # totp = pyotp.TOTP(user.key, interval=100)
        # otp = totp.now()
        # message = f"Your easebox confirmation code is {str(otp)}. Valid for 10 minutes, one-time use only."
        # sent = send_sms_msg(message, user.phone_number)

        return user
    
    def get_tokens(self, user):

        token = RefreshToken.for_user(user)

        data = {
            "access": str(token.access_token),
            "refresh": str(token)
        }
        return data
    
    def to_representation(self, instance: dict) -> dict:

        rep = super().to_representation(instance)

        for field in self.null_fields:
            try:
                if rep[field] is None:
                    rep.pop(field)
            except KeyError:
                pass

        return rep
            