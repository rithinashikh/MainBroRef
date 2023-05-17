from django.contrib import admin
from .models import *


@admin.register(Wishlist)
class CustomerAdmin(admin.ModelAdmin):
    model=Wishlist
