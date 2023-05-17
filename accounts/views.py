from django.shortcuts import render,redirect
from .forms import CustomUserForm,signinuserForm,otp_form
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from cart.models import Order
import uuid
import random
from .helpers import *
from .helpers import send_forget_password_mail
from cart.models import *
import json
from django.contrib.auth.views import LoginView
from cart.utils import Cookie_cart,Cart_address


@never_cache
def login_page(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                
                customer,created=Customer.objects.get_or_create(user=request.user,name=request.user.first_name,email=request.user.email)
                return redirect('/')
        else:
            return redirect('/accounts/logout')
    
    
    if request.method=='POST':
        email=request.POST.get('email')
        mobile='+91'+request.POST.get('mobile')
        print('this is my mobile number:',mobile)
        password=request.POST.get('password')
        user=authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            otp=str(random.randint(1000,9999))
            profile=User.objects.get(mobile=mobile)
            profile.otp=otp
            profile.save()
            obj=Message_Handler(mobile,otp)
            obj.send_otp()
            request.session['mobile'] = mobile
            return redirect('/accounts/otp-validation') 
            
        else:
            messages.warning(request,"Incorrect Credentials !!")
            
   
    form = signinuserForm()        
    try:
        cart=json.loads(request.COOKIES['cart'])
    except:
        cart={}

    no_items=0
    no_items=len(cart)   
    item_count=0
    context = {
        'form':form,
        'no_items':no_items,
        'item_count':item_count}
    return render(request, 'accounts/login.html',context)

@never_cache



def Register_page(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            return redirect('/')
        else:
            return redirect('/accounts/logout')
        
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        mobile='+91'+request.POST.get('mobile')
        print(type(mobile))
        check_user=User.objects.filter(mobile=mobile).first()
        print('check_user::',check_user)
        if check_user:
            messages.warning(request,"Mobile Number already exist !!") 
            return redirect('/accounts/signup')
        if form.is_valid():
            form.save()
            otp=str(random.randint(1000,9999))
            profile=User.objects.get(mobile=mobile)
            profile.otp=otp
            profile.save()
            obj=Message_Handler(mobile,otp)
            obj.send_otp()
            request.session['mobile'] = mobile
            return redirect('/accounts/otp-validation')
    else:
        form = CustomUserForm()
    try:
        cart=json.loads(request.COOKIES['cart'])
    except:
        cart={}

    no_items=0
    no_items=len(cart)  
    item_count=0 
    context = {
        'form':form,
        'no_items':no_items,
        'item_count':item_count,}

    return render(request, 'accounts/signup.html', context)

def LogoutPage(request):
    request.user.is_otp_verified=False
    request.user.save()
    logout(request)
    return redirect('/accounts/login')

def Forgot_password(request):
    try:
        if request.method == 'POST':
            email=request.POST.get('email')
        
            if not User.objects.filter(email=email).first():
                messages.warning(request,'Email is not registered!')
                return redirect('/accounts/forgot-password')
            user_obj=User.objects.get(email=email)
            print('user_obj:',user_obj)
            token=str(uuid.uuid4())
            print('token:',token)
            profile_obj=User.objects.get(email=email)
            profile_obj.forget_password_token=token
            profile_obj.save()
            
            print('profile_obj:',profile_obj)
            print('profile_obj token:',profile_obj.forget_password_token)
            send_forget_password_mail(profile_obj.email,token)
            messages.success(request,'An email has been sent !')
            return redirect('/accounts/forgot-password')
    except Exception as e:
        print(e)
    try:
        cart=json.loads(request.COOKIES['cart'])
    except:
        cart={}

    no_items=0
    no_items=len(cart) 
    item_count=0  
    context = {
        'no_items':no_items,
        'item_count':item_count}
    return render(request,'accounts/password.html',context)


def reset_password(request,token):
    context= {}

    try:
        profile_obj=User.objects.filter(forget_password_token=token).first()
        context = {'user_id':profile_obj.id}
        if request.method == 'POST':
            new_password=request.POST.get('Newpassword')
            confirm_password=request.POST.get('confirm_password2')
            user_id=request.POST.get('user_id')

            if user_id is None:
                messages.warning(request,'No user id is found')
                return redirect('/accounts/reset-password/{token}/')
            
            if new_password != confirm_password:
                messages.warning(request,'Passwords are not equal')
                return redirect('/accounts/reset-password/{token}/')
            
            user_obj=User.objects.get(id= user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/accounts/login')

        
        
    except Exception as e:
        print(e)
    try:
        cart=json.loads(request.COOKIES['cart'])
    except:
        cart={}

    no_items=0
    no_items=len(cart)   
    item_count=0
    context['no_items']=no_items
    context['item_count']=item_count
    return render(request,'accounts/reset_password.html',context)

def otp_validation(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            return redirect('/')

    mobile=request.session['mobile']
    context={'mobile':mobile}
    if request.method == 'POST':
        otp=request.POST.get('otp')
        profile=User.objects.filter(mobile=mobile).first()

        if otp == profile.otp:
            if profile.is_authenticated and not profile.is_superuser:
                profile.is_otp_verified=True
                profile.save()
                flag=True
                try:
                    cart=json.loads(request.COOKIES['cart'])
                except:
                    cart={}
                if cart:
                    cookieData=Cookie_cart(request)
                    items=cookieData['items']
                    order=cookieData['order']
                    no_items=cookieData['no_items']
                    item_count=0
                    address=[]

                    context={
                        'items':items,
                        'order':order,
                        'no_items':no_items,
                        'flag':flag,
                        'address':address,
                        'item_count':item_count,
                        
                    }
                    
                    
                    customer=request.user.customer
                    order, created=Order.objects.get_or_create(customer=customer,complete=False)
                    for item in items:
                        product=Products.objects.get(uid=item['product']['uid'])
                        product_variant=ProductVariant.objects.get(uid=item['uid'])
                        orderitem=OrderItem.objects.create(
                            product=product,
                            product_variant=product_variant,
                            order=order,
                            quantity=item['quantity'],
                        )
                    orderitem.ordered=False
                    orderitem.save()
                    items=order.orderitem_set.all()
                    for item in items:
                        if item.quantity>item.product_variant.quantity:
                            OrderItem.objects.get(uid=item.uid).delete()
                            messages.success(request,"Product removed as it sold out !!")
                    no_items=OrderItem.get_total_orderItems(request.user)
                    context={
                        'items':items,
                        'order':order,
                        'no_items':no_items,
                        'flag':flag,
                        }
                response=redirect('/')
                response.delete_cookie('cart')
                return response
                
        else:
            messages.warning(request,'Incorrect OTP')
            form = otp_form()
            return render(request,'accounts/otp.html', {'form':form})
    else:
        form = otp_form()
    try:
        cart=json.loads(request.COOKIES['cart'])
    except:
        cart={}

    no_items=0
    no_items=len(cart)   
    context = {
        'form':form,
        'no_items':no_items,}
    return render(request,'accounts/otp.html', context)

