import os
from twilio.rest import Client
from typing import Optional

# Auth credentials

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
account_phone = os.environ["TWILIO_PHONE"]

client = Client(account_sid, auth_token)


def send_sms_msg(msg: str, recipient: str) -> Optional[str]:

    message = client.messages.create(
        body=msg,
        from_=account_phone,
        to=recipient
    )

    if message.sid:
        return message.sid
    
    return False