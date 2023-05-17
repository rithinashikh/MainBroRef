from django.db import models
from base.models import BaseModel
from product.models import Products,ProductVariant
from cart.models import Order
import datetime
import pytz
from django.utils import timezone

from accounts.models import User

# Create your models here.

class Wishlist(BaseModel):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product=models.ForeignKey(Products,on_delete=models.CASCADE, null=True)
    date_added=models.DateTimeField(default=timezone.localtime)
    @classmethod
    def get_total_WishlistItems(cls):
        return cls.objects.all().count()