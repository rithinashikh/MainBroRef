from django.urls import path
from accounts.views import *


urlpatterns = [
    path('login/',login_page ,name='loginpage'),
    path('signup/',Register_page ,name='signup'),
    path('logout',LogoutPage,name='logout'),
    path('forgot-password/',Forgot_password,name='forgotpassword'),
    path('reset-password/<token>/',reset_password,name='resetpassword'),
    path('otp-validation',otp_validation,name='otp_validation'),
    
]