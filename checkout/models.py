from django.db import models
from accounts.models import User
from base.models import BaseModel
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        from cart.models import Order
        
        if self.is_default and self.user is not None and self.user.is_authenticated:
            # Set all other Address objects related to the same User instance to is_default=False
            self.__class__.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)
            order = Order.objects.get(customer=self.user.customer,complete=False)
            order.shipping_address=self
            order.save()
        super(Address, self).save(*args, **kwargs)
    
@receiver(post_save, sender=Address)
def set_default_address(sender, instance, **kwargs):
    from cart.models import Order

    # Check if there are any other Address objects for the same user
    other_addresses = Address.objects.filter(user=instance.user).exclude(pk=instance.pk)
    
    # If no other Address objects exist, set this one as the default
    if not other_addresses.exists() and not instance.is_default:
        instance.is_default = True
        order = Order.objects.get(customer=instance.user.customer,complete=False)
        order.shipping_address=instance
        order.save()
        instance.save()
    
    # If the default Address object was deleted, set the next available one as the default
    if not Address.objects.filter(user=instance.user, is_default=True).exists():
        next_available = Address.objects.filter(user=instance.user).order_by('created_at').first()
        if next_available:
            next_available.is_default = True
            order = Order.objects.get(customer=instance.user.customer,complete=False)
            order.shipping_address=next_available
            order.save()
            next_available.save()

@receiver(post_delete, sender=Address)
def delete_default_address(sender, instance, **kwargs):
    from cart.models import Order

    # If the default Address object was deleted, set the next available one as the default
    if instance.is_default:
        next_available = Address.objects.filter(user=instance.user).order_by('created_at').first()
        if next_available:
            next_available.is_default = True
            order = Order.objects.get(customer=instance.user.customer,complete=False)
            order.shipping_address=next_available
            order.save()
            next_available.save()
