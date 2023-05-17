from django.contrib import admin
from .models import *

# Register your models here.
# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display=['user','product','product_variant','cart_qty']
#     model=Cart

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    model=Customer

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['customer','date_ordered','shipping_address','status']
    model=Order
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=['product','product_variant','quantity']
    model=OrderItem

