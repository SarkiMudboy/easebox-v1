import smtplib, ssl
import os

port = os.environ["SMTP_PORT"]  # 465 For SSL
smtp_server = os.environ["SMTP_SERVER"]
sender_email = os.environ["EMAIL_ADDRESS"]  # Enter your address
app_password = os.environ["EMAIL_APP_PASSWORD"]

def send_mail(message, receiver_email):

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, message)