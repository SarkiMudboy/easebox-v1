from abc import abstractclassmethod, abstractmethod
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Dict, Optional, Any
from .abstract import Handler
from .verification import VerificationHandlerFactory
from abc import ABC

User = get_user_model()

class AccountHandlerFactory:

    def get(self, endpoint) -> object:

        endpoint_handlers = {
            "create-business-user": CreateBusinessUserHandler,
        }

        return endpoint_handlers[endpoint]()


class CreateBusinessUserHandler(Handler):

    def run(self, data: Dict[str, Any], *kwargs)-> Dict[str, Any]:

        data = self.transform(data)

        errors = self.validate(data)

        if errors:
            return errors
        
        data = self.create(data)

        self.verify_user(data, *kwargs)

        return self.response(data)
    
    def transform(self, data):

        data.pop("password2")

        return data
    
    def create(self, data):

        user = User.objects.create_user(**data)
        user.set_password(data["password"])
        user.save()

        data["token"] = self.get_tokens(user)
        data["id"] =  user.pk

        if user:
            return data
    
    def validate(self, data):

        return data # change later

    def verify_user(self, data, *kwargs):
        
        id_field = "email" if not data.get("phone_number") else "phone_number"
        data["request"] = kwargs.get("request")

        handler = VerificationHandlerFactory(id_field)
        handler.run(data)

    def get_tokens(self, user):

        token = RefreshToken.for_user(user)

        token = {
            "access": str(token.access_token),
            "refresh": str(token)
        }

        return token

    def response(self): ...
        