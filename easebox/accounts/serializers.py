from xml.dom import ValidationErr
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Business, User
from typing import Dict, Any



class UserSerializer(serializers.ModelSerializer):

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

    accept_terms_and_privacy = serializers.BooleanField(required=True)

    password = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "phone_number", "first_name", "last_name", "password", "password2", "accept_terms_and_privacy"]
        extra_kwargs = {"password": {"write_only": True}, "password2": {"write_only": True}}

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:

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


class BusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ["name", "address", "city", "state", "category"]
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:

        locations_provided = (attrs.get("address") and attrs.get("city") and attrs.get("state"))
        
        if attrs.get("name") and not locations_provided:
            raise serializers.ValidationError("Please provide address, city and state")
        
        return attrs


class RegisterBusinessUserSerializer(UserSerializer):

    business = BusinessSerializer(required=False)

    class Meta(UserSerializer.Meta):

        business_fields = ["business"]
        fields = UserSerializer.Meta.fields + business_fields



class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=False,
    )
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:

        if not attrs.get("email") and not attrs.get("phone_number"):
            raise serializers.ValidationError("Please provide an email or phone number")
        
        return attrs