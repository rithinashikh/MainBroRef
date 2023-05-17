from django import forms
from .models import Address
from cart.models import *

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'country', 'pincode', 'is_default')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'phone': forms.NumberInput(attrs={'placeholder': 'Enter your phone number'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter your address'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter your state'}),
            'country': forms.TextInput(attrs={'placeholder': 'Enter your country'}),
            'pincode': forms.NumberInput(attrs={'placeholder': 'Enter your pincode'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            self.add_error('phone', 'Phone number should only contain digits.')
        return phone

   

    def clean_pincode(self):
        pincode = self.cleaned_data['pincode']
        print('this is the pincode....',pincode,type(pincode))
        if not pincode.isdigit():
            raise forms.ValidationError("Pincode should only contain digits.")
        if len(pincode) != 6:
            raise forms.ValidationError("Pincode should be exactly 6 digits.")
        return pincode


   

    
class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(choices=Order.payment_choices, label='Payment Method',
                                       widget=forms.Select(attrs={'class': 'form-select'}))
    fields = ('payment_method',)

    