from django.contrib.auth.forms import UserCreationForm  

from .models import User
from django import forms




class CustomUserForm(UserCreationForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter First Name' }))
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Last Name' }))
    email=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter email address' }))
    mobile=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Your phonenumber' }))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-2','placeholder':'Enter password' }))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-2','placeholder':'Confirm password' }))
    class Meta:
        model = User
        fields =['first_name','last_name','email','mobile','password1','password2']

class signinuserForm(UserCreationForm):
    email=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter email address' }))
    mobile=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Your phonenumber' }))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-2','placeholder':'Enter password' }))

    class Meta:
        model = User
        fields=['email','mobile','password']

class otp_form(forms.Form):
    otp=forms.CharField(label='OTP',widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter OTP' }))
