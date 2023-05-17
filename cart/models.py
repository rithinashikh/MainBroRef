from django.db import models
from base.models import BaseModel
from accounts.models import User
from product.models import Products,ProductVariant,Coupon
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from checkout.models import *
from product.models import *
import datetime
import pytz




# Create your models here.
class Customer(BaseModel):
    user=models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class Order(BaseModel):
    customer=models.ForeignKey(Customer, on_delete=models.SET_NULL,null=True,blank=True)
    date_ordered=models.DateTimeField(default=timezone.localtime)
    complete=models.BooleanField(default=False)
    transaction_id=models.CharField(max_length=100,null=True)
    shipping_address=models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True)
    status_choices=(
        ('pending','pending'),
        ('processed','processed'),
        ('out for shipping','out for shipping'),
        ('canceled','canceled'),
        ('shipped','shipped'),
        ('out for delivery','out for delivery'),
        ('delivered','delivered'),
        ('returned','returned'),
        ('refunded','refunded'),
    )
    status=models.CharField(max_length=200,choices=status_choices,default='pending')
    payment_choices=(
        ('COD','COD'),
        ('Razorpay','Razorpay'),
        ('Paypal','Paypal'),
        
    )
    payment_method=models.CharField(max_length=200,choices=payment_choices,default='COD')
    delivery_date=models.DateField(null=True,blank=True)
    canceled_date=models.DateField(null=True,blank=True)
    returned_date=models.DateField(null=True,blank=True)
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,blank=True,null=True)
    offer_applied=models.BooleanField(default=False)
    @property
    def get_cart_total(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.get_total for item in orderitems])
        return total
    @property   
    def get_original_cart_total(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.get_orginal_total for item in orderitems])
        return total
    @property
    def get_total_offer_discount(self):
        orderitems=self.orderitem_set.all()
        discount=sum([item.get_offer_discount for item in orderitems])
        return discount
    
    @property
    def get_grand_total(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.get_total for item in orderitems])
        if self.coupon and not self.coupon.is_expired:
            if total>=self.coupon.minimum_amount:
                total=total-self.coupon.discount_price
        
        return total
    @property
    def get_discount(self):
        discount=0
        orderitems=self.orderitem_set.all()
        total=sum([item.get_total for item in orderitems])
        if self.coupon and not self.coupon.is_expired:
            if total>=self.coupon.minimum_amount:
                discount=self.coupon.discount_price

        return discount

    @property
    def get_cart_items(self):
        orderitems=self.orderitem_set.all()
        total=sum([item.quantity for item in orderitems])
        return total
    @classmethod
    def get_total_orders(cls):
        return cls.objects.count()
    def save(self, *args, **kwargs):
        if not self.customer:
            if self.user:
                self.customer = Customer.objects.create(
                    user=self.user,
                    name=self.user.first_name,
                    email=self.user.email)
            if Address.objects.all():
                address=Address.objects.get(is_default=True)
                self.shipping_address=address
        super().save(*args,**kwargs)
    def set_defaultaddress(self):
        if Address.objects.filter(is_default=True,user=self.customer.user):
            address=Address.objects.get(is_default=True,user=self.customer.user)
            self.shipping_address=address
              
    
class OrderItem(BaseModel):
    product=models.ForeignKey(Products,on_delete=models.CASCADE, null=True)
    product_variant=models.ForeignKey(ProductVariant,on_delete=models.SET_NULL,null=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField(default=0, null=True,blank=True)
    date_added=models.DateTimeField(default=timezone.localtime)
    ordered=models.BooleanField(default=False)
    offer=models.ForeignKey(Offer,on_delete=models.CASCADE,null=True,blank=True)
    is_offer_applied=models.BooleanField(default=False)
    

    @property
    def get_price(self):
        price=self.product.selling_price+self.product_variant.extra_price
        if self.offer:
            price=round(price*(1-(self.offer.discount/100)),2)
        return price
    @property
    def get_orginal_price(self):
        price=self.product.selling_price+self.product_variant.extra_price
        return price
    @property
    def get_offer_discount(self):
        price=self.product.selling_price+self.product_variant.extra_price
        discount=0
        if self.offer:
            discount=round(price*((self.offer.discount/100)),2)
        return discount
    @property
    def get_total(self):
        total=self.get_price*self.quantity
        return total
    @property
    def get_orginal_total(self):
        total=self.get_orginal_price*self.quantity
        return total
    @classmethod
    def get_total_orderItems(cls,user):
        return cls.objects.filter(ordered=False,order__customer__user=user).count()
    
    
    
    