from django.shortcuts import render,redirect,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from product.models import Products,Section
from cart.models import OrderItem,Customer
from checkout.models import Address
import json
from wishlist.models import *
from django.http import JsonResponse
from .forms import *
from checkout.forms import *
from django.core.paginator import Paginator

# Create your views here.
def Homepage(request):
    flag=False
    group=Section.objects.all()
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()
                flag=True
        else:
            return redirect('/accounts/logout')
    else:
        try:
            cart=json.loads(request.COOKIES['cart'])
        except:
            cart={}

        no_items=0
        no_items=len(cart) 
        item_count=0 
    products_list= Products.objects.filter(status=1)
    paginator = Paginator(products_list, 8) 
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
    "products":products,
    "flag" : flag,
    "group": group,
    'no_items':no_items,    
    'item_count':item_count,

        }
    avarage_rating={}
    for product in products:
        if Review.objects.filter(product=product):
            avarage_rating[product.uid] = round(Review.get_average_rating(product), 1)
    context['avarage_rating']=avarage_rating
    return render(request,'home/index.html',context)
    
def customer_account(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                user=request.user
                customer,created=Customer.objects.get_or_create(user=user)
                flag=True
                orders_list=[]
                address=[]
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()
                if Address.objects.filter(user=request.user,is_default=True):
                    address=Address.objects.get(user=request.user,is_default=True)
                if Order.objects.filter(customer=customer,complete=True):
                    orders_list=Order.objects.filter(customer=customer,complete=True).order_by('-date_ordered')
                paginator = Paginator(orders_list, 4) 
                page = request.GET.get('page')
                orders = paginator.get_page(page)
                context={
                    'user':user,
                    'customer':customer,
                    'flag':flag,
                    'no_items':no_items,
                    'item_count':item_count,
                    'address':address,
                    'orders':orders,

                }
                orderitems={}
                for order in orders:
                    if OrderItem.objects.filter(order=order):
                        orderitem=OrderItem.objects.filter(order=order)[0]
                        product=orderitem.product
                        orderitems[order.transaction_id]=product
                context['orderitems']=orderitems
                return render(request,'accounts/customer_account.html',context)
        else:
            return redirect('/accounts/logout')
    else:
        return redirect('/accounts/login')

def update_profile(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            request.user.image = image
            request.user.save()
            return JsonResponse({'image': request.user.image.url})
    return JsonResponse({'error': 'Invalid request'})

def personal_info(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                user=request.user
                customer=Customer.objects.get(user=user)
                flag=True
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()
                address=[]
                orders=[]
                if Address.objects.filter(user=request.user,is_default=True):
                    address=Address.objects.get(user=request.user,is_default=True)
                if Order.objects.filter(customer=customer,complete=True):
                    orders=Order.objects.filter(customer=customer,complete=True)
                
                context={
                    'user':user,
                    'customer':customer,
                    'flag':flag,
                    'no_items':no_items,
                    'item_count':item_count,
                    'address':address,
                    'orders':orders,

                }
                orderitems={}
                for order in orders:
                    if OrderItem.objects.filter(order=order):
                        orderitem=OrderItem.objects.filter(order=order)[0]
                        product=orderitem.product
                        orderitems[order.transaction_id]=product
                context['orderitems']=orderitems
                if request.method == 'POST':
                    profile_form = profileUpdate(request.POST, instance=user)
                    address_form=PersonAddress(request.POST,instance=address)
                    if profile_form.is_valid() and address_form.is_valid:
                        profile_form.save()
                        address_form.save()
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    profile_form = profileUpdate(instance=user)
                    if address:
                        address_form=PersonAddress(instance=address)
                    else:
                        address_form=PersonAddress()
                    context['profile_form']=profile_form
                    context['address_form']=address_form
                return render(request,'accounts/personal_info.html',context)
        else:
            return redirect('/accounts/logout')
    else:
        return redirect('/accounts/login')


     
def view_addressbook(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                user=request.user
                customer=Customer.objects.get(user=user)
                flag=True
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()
                address=[]
                orders=[]
                if Address.objects.filter(user=request.user,is_default=True):
                    address=Address.objects.get(user=request.user,is_default=True)
                address_book=Address.objects.filter(user=request.user)
                if Order.objects.filter(customer=customer,complete=True):
                    orders=Order.objects.filter(customer=customer,complete=True)
                
                context={
                    'user':user,
                    'customer':customer,
                    'flag':flag,
                    'no_items':no_items,
                    'item_count':item_count,
                    'address':address,
                    'orders':orders,
                    'address_book':address_book
                }
                
                
                return render(request,'accounts/manage_addressbook.html',context)
        else:
            return redirect('/accounts/logout')
    else:
        return redirect('/accounts/login')

def order_details(request,uid):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    context={}
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                customer=request.user.customer
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()
                context['item_count']=item_count
                context['no_items']=no_items
                flag=True
        else:
            return redirect('/accounts/logout')
    else:
        return redirect('/accounts/login')
    if Order.objects.get(customer=customer,complete=True,uid=uid):
        order=Order.objects.get(customer=customer,complete=True,uid=uid)
        items=order.orderitem_set.all()
        context['order']=order
        context['items']=items
        context['item_count']=item_count

        context['flag']=flag
        
    else:
        messages.warning(request,"No order summary !!")
    return render(request,'home/order_details.html',context)

def add_address(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    context={}
    flag=False
    context['flag']=flag
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                order, created=Order.objects.get_or_create(customer=request.user.customer,complete=False)
                no_items=OrderItem.get_total_orderItems(request.user)
                context['no_items']=no_items
                item_count=Wishlist.get_total_WishlistItems()
                context['item_count']=item_count
                flag=True
                
    
            if request.method == 'POST':
                form = AddressForm(request.POST)
                if form.is_valid():
                    address = form.save(commit=False)
                    address.user = request.user  # Assign the current user to the address
                    address.save()
                    return redirect('/address-book')
                else:
                    # Render the same form page with the invalid form data
                    context = {'form': form, 'form_data': request.POST}
                    return render(request, 'checkout/address.html', context)
            else:
                form = AddressForm()
                context['form']=form
            return render(request,'checkout/address.html',context)
    else:
        return redirect('/accounts/login')

def edit_address(request,uid):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                context={}
                no_items=OrderItem.get_total_orderItems(request.user)
                context['no_items']=no_items
                item_count=Wishlist.get_total_WishlistItems()
                context['item_count']=item_count
                address=Address.objects.get(uid=uid)

                if request.method == 'POST':
                    form = AddressForm(request.POST, instance=address)
                    
                    if form.is_valid():
                        form.save()
                        
                        return redirect('/address-book')
                else:
                    form = AddressForm(instance=address)
                    context['form']=form
                
                return render(request,'checkout/address.html',context)
    else:
        return redirect('/checkout/')

def delete_addresss(request,uid):
    Address.objects.get(uid=uid).delete()
    messages.success(request,"Address Deleted !!")
    return redirect('/address-book')

def privacy_settings(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                user=request.user
                customer=Customer.objects.get(user=user)
                flag=True
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()

                if Address.objects.get(user=request.user,is_default=True):
                    address=Address.objects.get(user=request.user,is_default=True)
                
                context={
                    'user':user,
                    'customer':customer,
                    'flag':flag,
                    'no_items':no_items,
                    'item_count':item_count,
                    'address':address,
                }
                try:
                    if request.method == 'POST':
                        current_password=request.POST.get('current_password')
                        new_password=request.POST.get('new_pass1')
                        confirm_password=request.POST.get('new_pass2')
                        if user.check_password(current_password):
                            if new_password != confirm_password:
                                messages.warning(request,'Passwords are not equal')
                                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                            else:
                                user.set_password(new_password)
                                user.save()
                                messages.success(request,'Password changed')
                        else:
                            messages.warning(request,"Incorrect password !!")
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                except Exception as e:
                    print(e)
                
                return render(request,'accounts/privacy_settings.html',context)
        else:
            return redirect('/accounts/logout')
    else:
        return redirect('/accounts/login')