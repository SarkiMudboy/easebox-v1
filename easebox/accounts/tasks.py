from celery import shared_task
from abstract.services.email.email_local import Email

@shared_task()
def send_verification_mail(*args) -> None:

    mail = Email(*args)
    mail.send()