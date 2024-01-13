from abc import abstractclassmethod, abstractmethod
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractBaseUser
from typing import Dict, Optional, Any
from .abstract import Handler

from .verification import VerificationHandlerFactory
from ..validation.models import BusinessUser
from ..validation.validators import handle_errors

from abc import ABC
from pydantic import ValidationError

User: AbstractBaseUser = get_user_model()

class AccountHandlerFactory(object):

    @staticmethod
    def get(endpoint: str) -> Handler:

        endpoint_handlers = {
            "create-business-user": CreateBusinessUserHandler,
        }

        return endpoint_handlers[endpoint]()


class CreateBusinessUserHandler(Handler):

    def run(self, data: Dict[str, Any], **kwargs)-> Dict[str, Any]:

        data = self.transform(data)

        data, errors = self.validate(data)

        if errors:
            return data, errors
        
        data = self.create(data)

        self.verify_user(data, **kwargs)

        return self.response(data)
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:

        if data.get("password2"):
            data.pop("password2")

        return data
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:

        user = User.objects.create_user(**data)
        user.save()

        data["token"] = self.get_tokens(user)
        data["id"] =  user.pk

        if user:
            return data
    
    def validate(self, data: Dict[str, Any]):

        try:
            BusinessUser.model_validate(data)
        except ValidationError as e:

            error = handle_errors(e.errors())
            # print(error)
            return data, error

        return data, None

    def verify_user(self, data: Dict[str, Any], **kwargs) -> None:

        # If the user provides both email and phone number, we don't need to handle verification here 
        # The verification endpoints will be used instead as the user will choose preffered channel

        if data.get("phone_number") and data.get("email"):
            return
        
        # if not, proceed...

        id_field = "email" if not data.get("phone_number") else "phone"
        data["request"] = kwargs.get("request")

        handler = VerificationHandlerFactory.get(id_field)
        handler.run(data)

    def get_tokens(self, user: AbstractBaseUser) -> str:

        token = RefreshToken.for_user(user)

        token = {
            "access": str(token.access_token),
            "refresh": str(token)
        }

        return token

    def response(self, data):
        return data, None
        