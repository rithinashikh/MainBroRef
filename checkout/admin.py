from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email',  'address', 'is_default')
