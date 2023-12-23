from .abstract import Handler
from typing import Dict, Optional, Any, List
from django.contrib.auth import get_user_model
from ..verification.email.verify_email import verify_email

User = get_user_model()

class VerificationHandlerFactory(object):

    @staticmethod
    def get(endpoint: str) -> Handler:

        enpoint_handlers = {
            "email": EmailVerificationHandler,
            "phone": PhoneNumberVerificationHandler,
        }

        return enpoint_handlers[endpoint]()
    


class EmailVerificationHandler(Handler):
    
    def run(self, data, *kwargs):

        self.validate(data)
        
        self.verify(data)

        return self.response(data)
    
    def validate(self, data):
        pass

    def verify(self, data: Dict[str, Any]):

        request = data.pop("request")
        user = User.objects.get(id=data.get("id"))

        verify_email(request, user)

    def response(self, data):
        return None


class PhoneNumberVerificationHandler(Handler):
    pass