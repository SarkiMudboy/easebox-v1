from xml.dom import ValidationErr
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import User
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

    password = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "phone_number", "first_name", "last_name", "password", "password2"]
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
    
    def to_representation(self, instance: dict) -> dict:

        rep = super().to_representation(instance)

        for field in self.null_fields:
            try:
                if rep[field] is None:
                    rep.pop(field)
            except KeyError:
                pass

        return rep
            