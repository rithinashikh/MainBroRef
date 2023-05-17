from django.urls import path
from home.views import *


urlpatterns = [
    path('', Homepage ,name='homepage'),
    path('account-details',customer_account,name='customer_account'),
    path('personal-details',personal_info,name='personal_info'),
    path('address-book',view_addressbook,name='view_addressbook'),
    path('order_details  <uuid:uid>', order_details ,name='order_details'),  
    path('edit-add  <uuid:uid>', edit_address ,name='add_edit'),  
    path('delete-add  <uuid:uid>', delete_addresss ,name='add_delete'),  
    path('add-new-address', add_address ,name='add_new_address'),  
    path('privacy-settings', privacy_settings ,name='privacy_settings'),  


]