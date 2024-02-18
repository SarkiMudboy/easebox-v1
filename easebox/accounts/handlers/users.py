from abc import abstractclassmethod, abstractmethod
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractBaseUser
from typing import Dict, Optional, Any, Tuple
from .abstract import Handler

from ..models import Business

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

        user_business = data.get("business")

        if user_business:
            data["business"] = dict(user_business) 
        
        return data
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:

        user_business = None

        if data.get('business'):
            user_business = data.pop("business")

        user = User.objects.create_user(**data)

        if user:
            if user_business:
                business = self.create_business(user, user_business)
                data["business"] = business.name
                
            data["token"] = self.get_tokens(user)
            data["id"] =  user.pk

            return data
    
    def create_business(self, user: AbstractBaseUser, business_data: Dict[str, Any]) -> None:

        business = Business.objects.create(owner=user, **business_data)
        return business

    def validate(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], None]:

        try:
            BusinessUser.model_validate(data)
        except ValidationError as e:

            error = handle_errors(e.errors())
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
        
