from django.urls import path
from cart.views import *


urlpatterns = [
    path('', cartpage ,name='cartpage'),  
    path('delete-cartitem <uuid:uid>',product_delete,name='cartitem_delete'),
    path('remove-coupon <uuid:uid>', remove_coupon,name='remove_coupon'),
    

]