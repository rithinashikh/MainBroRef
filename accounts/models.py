from django.db import models
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    username=None
    email = models.EmailField(unique=True)
    image=models.ImageField(upload_to='profiles',blank=True,null=True)
    mobile=PhoneNumberField(region='IN')
    is_verified=models.BooleanField(default=False)
    is_otp_verified=models.BooleanField(default=False)
    email_token=models.CharField(max_length=100,null=True,blank=True)
    forget_password_token=models.CharField(max_length=100,null=True,blank=True)
    last_login_time=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    last_logout_time=models.DateTimeField(null=True,blank=True)
    last_updated_time=models.DateTimeField(auto_now=True,null=True,blank=True)
    otp=models.CharField(max_length=100,null=True,blank=True)
    is_blocked=models.BooleanField(default=False)


    objects=UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    