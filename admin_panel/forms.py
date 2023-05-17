from django.contrib.auth.forms import UserCreationForm  
from product.models import *
from accounts.models import User
from django import forms
from django.forms.models import inlineformset_factory
from checkout.models import Address
from .models import *


class signinuserForm(UserCreationForm):
    email=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter email address' }))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control my-2','placeholder':'Enter password' }))

    class Meta:
        model = User
        fields=['email','password']



class CustomUpdateForm(forms.ModelForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter First Name' }))
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Last Name' }))
    email=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter email address' }))
    mobile=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Your phonenumber' }))
    is_blocked=forms.BooleanField(required=False)
    class Meta:
        model = User
        fields =['first_name','last_name','email','mobile','is_blocked']

class ProductUpdateForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Name of Product' }))
    section=forms.ModelMultipleChoiceField(queryset=Section.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    Sub_group=forms.ModelMultipleChoiceField(queryset=Sub_groups.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'form-control'}),required=False)
    category=forms.ModelChoiceField(queryset=Category.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    small_description=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'small description'}))
    description=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Description'}))
    specification=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Specificaiton'}))
    original_price=forms.FloatField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Original Price'}))
    selling_price=forms.FloatField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Selling Price'}))
    status=forms.BooleanField(required=False)
    trending=forms.BooleanField(required=False)
    meta_title=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Meta title'}))
    meta_keywords=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Meta Keywords'}))
    meta_description=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Meta Descritption'}))
    brand=forms.ModelMultipleChoiceField(queryset=Brand.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'form-control'}),required=False)
    tag_product=forms.ModelMultipleChoiceField(queryset=Tags.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'form-control'}),required=False)
    offer=forms.ModelChoiceField(queryset=Offer.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}),required=False)
    
    class Meta:
        model = Products
        fields =['name','brand','section','Sub_group','category','small_description','tag_product','description','original_price',
                 'selling_price','status','trending','meta_title',
                 'meta_keywords','meta_description','offer','specification',
                 
                 ]

class ProductImageForm(forms.ModelForm):
    img = forms.ImageField()

    class Meta:
        model=ProductImage
        fields=['img']
class ProductVariantForm(forms.ModelForm):
    color=forms.ModelChoiceField(queryset=Color.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    size=forms.ModelChoiceField(queryset=Size.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    by_age=forms.ModelChoiceField(queryset=By_Age.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    extra_price = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}),initial=0)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}),initial=0)

    class Meta:
        model=ProductVariant
        fields=['color', 'size', 'by_age', 'extra_price', 'quantity']



ProductVariantFormSet = inlineformset_factory(
        Products, ProductVariant, form=ProductVariantForm, extra=1, can_delete=True
    )
ProductImageFormSet = inlineformset_factory(
        Products, ProductImage, form=ProductImageForm, extra=1, can_delete=True
    )


class CategoryUpdateForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Name of Category' }))
    img = forms.ImageField()
    description=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Description'}))
    status=forms.BooleanField(required=False)
    trending=forms.BooleanField(required=False)
    meta_title=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Meta title'}))
    meta_keywords=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Meta Keywords'}))
    meta_description=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Meta Descritption'}))
    offer=forms.ModelChoiceField(queryset=Offer.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Category
        fields =['name','img','description',
                 'status','trending','meta_title',
                 'meta_keywords','meta_description', 'offer',     
        ]
        widgets = {
            'img': forms.ClearableFileInput(attrs={'multiple': True},),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['offer'].required = False

class AddCoupon(forms.ModelForm):
    coupon_code=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter coupon code' }))
    description=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Description'}))
    is_expired=forms.BooleanField(required=False)
    discount_price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}),initial=100)
    minimum_amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}),initial=500)


    class Meta:
        model = Coupon
        fields =['coupon_code','description',
                 'is_expired','discount_price',
                 'minimum_amount',     
        ]

class AddOffer(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter name of offer' }))
    is_active=forms.BooleanField(required=False)
    discount = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Offer
        fields =['name','is_active',
                 'discount',    
        ]

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

class Bank_details(forms.ModelForm):
    account_holder=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter name' }))
    bank=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter your bank' }))
    branch=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter branch' }))
    IFSC=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter IFSC' }))
    account_number=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter account_number' }))
    Upi=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Upi' }))


    class Meta:
        model = Admin_Bank_Details
        fields = [ 'account_holder', 'bank', 'branch', 'IFSC', 'account_number','Upi','is_default']
        
        widgets = {
                    'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                }


class SectionUpdateForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Name of Section' }))
    img = forms.ImageField()
    

    class Meta:
        model = Section
        fields =['name','img',      
        ]
        
class SubsectionUpdateForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Name of Sub section' }))
    

    class Meta:
        model = Sub_groups
        fields =['name',      
        ]

class BrandUpdationForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Name of Brand' }))
    offer=forms.ModelChoiceField(queryset=Offer.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    

    class Meta:
        model = Brand
        fields =['name','offer',    
        ]       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['offer'].required = False

class ColorUpdationForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Color' }))
    

    class Meta:
        model = Color
        fields =['name',      
        ]       
class SizeUpdationForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter Size' }))
    

    class Meta:
        model = Size
        fields =['name',      
        ]       

class AgeUpdationForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter age-range' }))

    class Meta:
        model = By_Age
        fields =['name',      
        ]       

class TagUpdationForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control my-2','placeholder':'Enter name of tag' }))

    class Meta:
        model = Tags
        fields =['name',      
        ]       