from django.conf import settings
from twilio.rest import Client
from django.core.mail import send_mail
import os

account_sid = os.environ.get('account_sid')
auth_token = os.environ.get('auth_token')

class Message_Handler:
    mobile=None
    otp=None
    def __init__(self, mobile,otp) -> None:
        self.mobile=mobile
        self.otp=otp
    def send_otp(self):

        client = Client(account_sid , auth_token)
        message = client.messages.create(
        body=f"Your OTP is {self.otp}",
        from_="+14752655839",
        to=self.mobile
)

def send_forget_password_mail(email,token):
    subject='Link to reset Your new password | Cartify Shopping site'
    message=f'Hi, Greetings,click on the link to reset your password http://127.0.0.1:8000/accounts/reset-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    print(email_from)
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True
