from .abstract import Handler
from typing import Dict, Optional, Any, List
from django.contrib.auth import get_user_model
from ..verification.email.verify_email import verify_email

User = get_user_model()

class VerificationHandlerFactory(object):

    def get(self, endpoint):

        enpoint_handlers = {
            "email": EmailVerificationHandler,
            "phone": PhoneNumberVerificationHandler,
        }

        return enpoint_handlers[endpoint]()
    


class EmailVerificationHandler(Handler):
    
    def run(self, data, *kwargs):

        self.validate(data)
        
        self.verify(data)

        return self.response()
    
    def validate(self, data):
        pass

    def verify(self, data: Dict[str, Any]):

        request = data.get("request")
        user = User.objects.get(id=user.id)

        verify_email(request, user)

    def response(self, data):
        pass


class PhoneNumberVerificationHandler(Handler):
    pass