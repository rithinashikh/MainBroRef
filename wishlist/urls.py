from django.urls import path
from .views import *


urlpatterns = [
    path('', view_wishlist ,name='view_wishlist'),  
   
]