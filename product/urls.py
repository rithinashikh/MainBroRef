from django.urls import path
from product.views import *


urlpatterns = [
    path('<slug>/', products_details ,name='product-details'),  
    path('shop/<slug>/', group_view ,name='group_view'),  
    path('category_filter/<name>', cateogory_view ,name='category_view'),  
    path('shop',shop,name='shop')

]