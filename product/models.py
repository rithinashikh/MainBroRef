from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
import uuid
from django.utils import timezone
from datetime import datetime
from accounts.models import User
import datetime
from django.db.models import Avg


#Create your models here.
class Offer(BaseModel):
    name=models.CharField(max_length=100,null=True)
    discount=models.FloatField()
    active=models.BooleanField(default=False)
    

    def __str__(self):
        return self.name

class Category(BaseModel):
    name=models.CharField(max_length=100)
    img=models.ImageField(upload_to="categories")
    slug=models.SlugField(unique=True,null=True,blank=True)
    description=models.TextField(max_length=500,null=False,blank=False)
    status=models.BooleanField(default=False,help_text="0=default, 1=Hidden")
    trending=models.BooleanField(default=False,help_text="0=default, 1=trending")
    meta_title=models.CharField(max_length=150,null=False,blank=False)
    meta_keywords=models.CharField(max_length=150,null=False,blank=False)
    meta_description=models.TextField(max_length=500,null=False,blank=False)
    created_at=models.DateTimeField(default=timezone.localtime)
    offer=models.ForeignKey(Offer,on_delete=models.SET_NULL,null=True,blank=True)


    def __str__(self) -> str:
        return self.name

    def save(self,*args,**kwargs):
        
        self.slug=slugify(self.name)
        super(Category, self).save(*args,**kwargs)


class Products(BaseModel):
    name=models.CharField(max_length=100)
    slug=models.SlugField(unique=True,null=True,blank=True)
    section=models.ManyToManyField('Section')
    Sub_group=models.ManyToManyField('Sub_groups',blank=True)
    category=models.ForeignKey(Category, on_delete=models.CASCADE,related_name="products")
    small_description=models.CharField(max_length=200,null=False,blank=False)
    description=models.TextField(max_length=500,null=False,blank=False)
    original_price=models.FloatField(null=False,blank=False)
    selling_price=models.FloatField(null=False,blank=False)
    status=models.BooleanField(default=False,help_text="0=default, 1=Hidden")
    trending=models.BooleanField(default=False,help_text="0=default, 1=trending")
    meta_title=models.CharField(max_length=150,null=False,blank=False)
    meta_keywords=models.CharField(max_length=150,null=False,blank=False)
    meta_description=models.TextField(max_length=500,null=False,blank=False)
    created_at=models.DateTimeField(default=timezone.localtime)
    brand=models.ManyToManyField("Brand",blank=True)
    tag_product=models.ManyToManyField('Tags',blank=True)
    offer=models.ForeignKey(Offer,on_delete=models.SET_NULL,null=True,blank=True)
    specification=models.TextField(max_length=500,null=True,blank=True)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super(Products, self).save(*args,**kwargs)

    def __str__(self) -> str:
        return self.name  
    def get_product_price_by_variants(self,size):
        return int(self.selling_price *(Size.objects.get(name=size).price)/100)
    def get_extra_price_by_color(self,color):
        return int(self.selling_price*Color.objects.get(name=color).price/100)
class Brand(BaseModel):
    name=models.CharField(max_length=100)
    offer=models.ForeignKey(Offer,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self) -> str:
        return self.name
    
    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super(Brand, self).save(*args,**kwargs)


class Color(BaseModel):

    name=models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return self.name
    
class Size(BaseModel):
    name=models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name
    
class By_Age(BaseModel):
    name=models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name
    
class Section(BaseModel):
    name=models.CharField(max_length=100)
    img=models.ImageField(upload_to="groups")
    slug=models.SlugField(unique=True,null=True,blank=True)
    def __str__(self) -> str:
        return self.name
    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super(Section, self).save(*args,**kwargs)



class ProductVariant(BaseModel): 
    product=models.ForeignKey(Products, on_delete=models.CASCADE,related_name="product_variant")
    color=models.ForeignKey(Color,on_delete=models.CASCADE)
    size=models.ForeignKey(Size,on_delete=models.CASCADE)
    extra_price=models.FloatField(default=0)
    quantity=models.IntegerField(default=0)
    by_age=models.ForeignKey(By_Age,on_delete=models.CASCADE)
    class Meta:
        unique_together = ('product', 'size', 'color','by_age')
    
    def __str__(self) -> str:
        return self.color.name+':'+self.size.name+ ':'+self.by_age.name

class Images_product(BaseModel):
    variant=models.ForeignKey(ProductVariant, on_delete=models.CASCADE,related_name="variant_images")
    img=models.ImageField(upload_to='Variant_images')

class ProductImage(BaseModel):
    product=models.ForeignKey(Products, on_delete=models.CASCADE,related_name="product_images")
    img=models.ImageField(upload_to="products")

class Sub_groups(BaseModel):
    name=models.CharField(max_length=100)
    def __str__(self) -> str:
        return self.name

class Tags(BaseModel):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Coupon(BaseModel):
    coupon_code=models.CharField(max_length=20)
    is_expired=models.BooleanField(default=False)
    discount_price=models.IntegerField(default=100)
    minimum_amount=models.IntegerField(default=500)
    description=models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        return self.coupon_code

class Review(BaseModel):
    CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    product=models.ForeignKey(Products, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    comment=models.TextField(max_length=500,null=True,blank=True)
    rating=models.FloatField(choices=CHOICES,null=False,blank=False)
    added_at=models.DateTimeField(default=timezone.localtime)

    @classmethod
    def get_average_rating(cls, product):
        return cls.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    def __str__(self):
        return self.user.first_name +':'+ self.product.name