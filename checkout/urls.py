from django.urls import path
from .views import *


urlpatterns = [
    path('', checkout ,name='checkout'),  
    path('address', add_address ,name='add_address'),  
    path('edit-address <uuid:uid>', edit_address ,name='edit_address'),  
    path('delete-address <uuid:uid>', delete_addresss ,name='delete_address'),
    path('edit-address ', edit_session_address ,name='edit_session_address'),  
    path('delete-address ', delete_session_address ,name='delete_session_address'),
    path('paypal-payment',paypal_payment,name='paypal_payment'),
    path('payment', paymentpage ,name='paymentpage'),  
    

]