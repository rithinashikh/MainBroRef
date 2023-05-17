from django.contrib.auth.forms import UserCreationForm  
from product.models import *
from accounts.models import User
from django import forms
from django.forms.models import inlineformset_factory
from checkout.models import Address


class profileUpdate(forms.ModelForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter First Name' }))
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Last Name' }))
    email=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter email address' }))
    mobile=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Your phonenumber' }))
    class Meta:
        model = User
        fields =['first_name','last_name','email','mobile']

class PersonAddress(forms.ModelForm):
    address=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter your address' }))
    city=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter your city' }))
    state=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter your state' }))
    country=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter your country' }))
    pincode=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter your pincode' }))

    class Meta:
        model = Address
        fields = [ 'address', 'city', 'state', 'country', 'pincode']
        


