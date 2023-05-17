from django.conf import settings
from twilio.rest import Client


account_sid = "ACb50019c56d73d943024b58fbed88b31d"
auth_token = "e6e354ff40656e952d736585217e6091"

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587 
# EMAIL_HOST_USER = 'cartifyshopping23@gmail.com'
# EMAIL_HOST_PASSWORD = 'sou@5503'



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


