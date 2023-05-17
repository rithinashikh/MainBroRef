from django.urls import path
from .views import *


urlpatterns = [
    path('', view_orders ,name='view_order'),  
    path('summary  <uuid:uid>', order_summary ,name='order_summary'),  
    path('cancel-order  <uuid:uid>', cancel_order ,name='cancel_order'),  
    path('return-order  <uuid:uid>', return_order ,name='return_order'),  
    

]