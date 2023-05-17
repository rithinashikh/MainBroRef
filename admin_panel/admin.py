from django.contrib import admin
from .models import Admin_Bank_Details

@admin.register(Admin_Bank_Details)
class Admin_Bank_DetailsAdmin(admin.ModelAdmin):
    list_display = ('account_holder', 'bank', 'branch', 'is_default')
