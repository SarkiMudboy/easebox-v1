import smtplib, ssl
from django.core.mail import send_mail
from django.conf import settings
import os


class Email(object):

    def __init__(self, subject: str, message: str, to: str) -> None:

        self.message = message
        self.subject = subject
        self.to = to
        self.from_email = settings.DEFAULT_FROM_EMAIL

    def send(self):

        try:

            send_mail(subject=self.subject, message=self.message, 
                    from_email=self.from_email, recipient_list=[self.to], fail_silently=False)
            
        except Exception as e:
            print(str(e))
        