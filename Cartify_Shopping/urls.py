"""Cartify_Shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from cart.views import *
from checkout.views import *
from product.views import *
from wishlist.views import *
from admin_panel.views import *
from home.views import *
from admin_panel.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('accounts.urls')),
    path('',include('home.urls')),
    path('products/',include('product.urls')),
    path('admin-panel/',include('admin_panel.urls')),
    path('add-to-cart/',add_to_cart ,name='add_to_cart'),
    path('add-to-wishlist/',add_to_wishlist ,name='add_to_wishlist'),
    path('delete-from-wishlist/',delete_from_wishlist ,name='delete_from_wishlist'),
    path('update-shippingaddress/', updateshippingaddress ,name='updateshippingaddress'),  
    path('cart/',include('cart.urls')),
    path('checkout/',include('checkout.urls')),
    path('filter-data', filter_data ,name='filter_data'),  
    path('sort-data', sort_data ,name='sort_data'),  
    path('order/',include('orders.urls')),
    path('update-order/',update_order,name='update_order'),
    path('update-coupon/',update_coupon,name='update_coupon'),
    path('wishlist/',include('wishlist.urls')),
    path('proceed-to-pay',razorpaycheck,name='razorpaycheck'),
    path('payment-method/',payment_method,name='payment_method'),
    path('paypal-method/',paypal_method,name='paypal_method'),
    path('update-profile/',update_profile,name='update_profile'),
    path('update-admin-profile/',update_admin_profile,name='update_admin_profile'),
    path('add-offer/',add_offer,name='add_offer'),
    path('product-list',product_list,name="product_list"),
    path('search-product',searchproduct,name='searchproduct'),
    path('admin-panel-products',admin_panel_products,name="admin_panel_products"),
    path('admin-panel-customers',admin_panel_customers,name="admin_panel_customers"),
    path('admin-panel-coupons',coupons_list_admin,name="coupons_list_admin"),
    path('admin-panel-category',category_list_admin,name="category_list_admin"),
    path('admin-panel-offers',offers_list_admin,name="offers_list_admin"),
    path('update-offer/',update_offer,name='update_offer'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    
urlpatterns+=staticfiles_urlpatterns()
