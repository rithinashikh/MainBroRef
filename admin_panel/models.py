from django.db import models
from accounts.models import User
from base.models import BaseModel
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Admin_Bank_Details(BaseModel):
    admin = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    account_holder = models.CharField(max_length=50)
    bank = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    IFSC = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    Upi = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account_holder} - {self.bank}"
    
    def save(self, *args, **kwargs):
        
        if self.is_default and self.admin is not None and self.admin.is_authenticated and self.admin.is_superuser:
            # Set all other address objects related to the same admin instance to is_default=False
            self.__class__.objects.filter(admin=self.admin).exclude(pk=self.pk).update(is_default=False)
            
        super(Admin_Bank_Details, self).save(*args, **kwargs)
    
@receiver(post_save, sender=Admin_Bank_Details)
def set_default_account(sender, instance, **kwargs):

    # Check if there are any other account objects for the same user
    other_accounts = Admin_Bank_Details.objects.filter(admin=instance.admin).exclude(pk=instance.pk)
    
    # If no other acc objects exist, set this one as the default
    if not other_accounts.exists() and not instance.is_default:
        instance.is_default = True
        
    
    # If the default acc object was deleted, set the next available one as the default
    if not Admin_Bank_Details.objects.filter(admin=instance.admin, is_default=True).exists():
        next_available = Admin_Bank_Details.objects.filter(admin=instance.admin).order_by('created_at').first()
        if next_available:
            next_available.is_default = True
            next_available.save()

@receiver(post_delete, sender=Admin_Bank_Details)
def delete_default_account(sender, instance, **kwargs):
    # If the default account object was deleted, set the next available one as the default
    if instance.is_default:
        next_available = Admin_Bank_Details.objects.filter(admin=instance.admin).order_by('created_at').first()
        if next_available:
            next_available.is_default = True
            next_available.save()
