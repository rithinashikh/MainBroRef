from django.http import  Http404,HttpResponse,HttpResponseRedirect,JsonResponse
from django.shortcuts import redirect,render
from django.contrib import messages
from product.models import *
from cart.models import *
from accounts.models import User
from django.contrib.auth.decorators import login_required
from .forms import *
import json
from datetime import datetime, timedelta
from django.utils import timezone
import random
from cart.utils import Cookie_cart,Cart_address
import uuid
from wishlist.models import *

# Create your views here.
def checkout(request):
    flag=False
    if request.user.is_superuser:
            return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                customer=request.user.customer
                customer.name=request.user.first_name
                customer.save()
                flag=True
                try:
                    order=Order.objects.get(customer=customer,complete=False)
                    items=order.orderitem_set.all()
                    if not items:
                        Order.objects.get(customer=customer,complete=False).delete()
                        messages.warning(request,"Your cart is empty, cartify some !!")

                        return redirect('/')
                except:
                    return redirect('/')
                for item in items:
                    if item.quantity>item.product_variant.quantity:
                        OrderItem.objects.get(uid=item.uid).delete()
                        messages.success(request,"Product removed as it sold out !!")
                no_items=OrderItem.get_total_orderItems(request.user)
                address=Address.objects.filter(user=request.user)

                context={
                    'items':items,
                    'order':order,
                    'no_items':no_items,
                    'address':address,
                    'flag':flag,
                }
                available_offers={}
                for item in items:
                    available_offers[item]=[]
                offer_discount=0
                greatestoffer=None
                for item in items:
                    if item.product.offer:
                        available_offers[item].append(item.product.offer)
                    if item.product.category.offer:
                        available_offers[item].append(item.product.category.offer)
                    if item.product.brand.first().offer:
                        available_offers[item].append(item.product.brand.first().offer)
                if available_offers:
                    for item,offers in available_offers.items():
                        for offer in offers:
                            if offer.discount>offer_discount:
                                offer_discount=offer.discount
                                greatestoffer=offer
                context['offer']=greatestoffer
                
                item_count=Wishlist.get_total_WishlistItems()
                context['item_count']=item_count
                if order:  
                    return render(request,'checkout/checkout.html',context)
                else:
                    return redirect('/')
        else:
            return redirect('/accounts/logout')
    else:
        cookieData=Cookie_cart(request)
        items=cookieData['items']
        order=cookieData['order']
        no_items=cookieData['no_items']
        item_count=cookieData['item_count']
        address=[]

        context={
            'items':items,
            'order':order,
            'no_items':no_items,
            'flag':flag,
            'address':address,
             'item_count':item_count,
            
        }
        context['item_count']=0
        if 'add' in request.session:
    
            add= request.session['add']
            add['uid']=uuid.UUID(add['uid'])
            address.append(add)
            context['address']=address
        

        if not items:
            messages.warning(request,"Your cart is empty, cartify some !!")
            return redirect('/')
        return render(request,'checkout/checkout.html',context)     

def add_address(request):
    context={}
    flag=False
    context['flag']=flag
    if request.user.is_superuser:
         return redirect('/accounts/logout')
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
                form.clean_pincode()
                address = form.save(commit=False)
                
                if request.user.is_authenticated:
                    address.user = request.user  # Assign the current user to the address
                    address.save()
                else:
                    messages.warning(request,"Please Login to continue!!")
                return redirect('/checkout') 
            else:
                # Render the same form page with the invalid form data
                context = {'form': form, 'form_data': request.POST}
                return render(request, 'checkout/address.html', context)
        else:
            form = AddressForm()
            context['form']=form
        return render(request,'checkout/address.html',context)
    else:
        cookieData=Cookie_cart(request)
        items=cookieData['items']
        order=cookieData['order']
        no_items=cookieData['no_items']

        context={
            'items':items,
            'order':order,
            'no_items':no_items,
            'flag':flag,
           
        }
        if request.method == 'POST':
            add=Cart_address(request)
            if not add['pincode'].isdigit() or len(add['pincode']) != 6:
                context['address'] = add
                messages.warning(request,"Invalid entry for pincode !!")
                return render(request,'checkout/guestaddress.html',context)
            if not add['phone'].isdigit() or len(add['phone']) != 10:
                context['address'] = add
                messages.warning(request,"Invalid phonenumber !!")
                return render(request,'checkout/guestaddress.html',context)
            address=[]
            address.append(add)
            request.session['add']=add
            context['address']=address
            return render(request,'checkout/checkout.html',context)
        else:
            return render(request,'checkout/guestaddress.html',context)
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
                        
                        return redirect('/checkout/')
                else:
                    form = AddressForm(instance=address)
                    context['form']=form
                
                return render(request,'checkout/address.html',context)
    else:
        return redirect('/checkout/')
def edit_session_address(request):
    context={}
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if 'add' in request.session:
        context['address'] = request.session['add']
    if request.method == 'POST':
            add=Cart_address(request)
            request.session['add']=add
            context['address'] = request.session['add']
            return redirect('/checkout/')
    return render(request,'checkout/guestaddress.html',context)
def delete_addresss(request,uid):
    Address.objects.get(uid=uid).delete()
    messages.success(request,"Address Deleted !!")
    return redirect('/checkout/')
def delete_session_address(request):
    del request.session['add']
    return redirect('/checkout/')
def updateshippingaddress(request):
    data=json.loads(request.body)
    address_uid=data['address_uid']
    if request.user.is_authenticated:
        customer=request.user.customer
        order=Order.objects.get(customer=customer,complete=False)
        address=Address.objects.get(uid=address_uid)
        order.shipping_address=address
        order.save()
        return JsonResponse('address added',safe=False)
    else:
        return JsonResponse('Need to login to continue',safe=False)
def paymentpage(request):
    flag=False
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                address=Address.objects.filter(user=request.user)
                if not address:
                    messages.warning(request,"add address to continue !!")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
                customer=request.user.customer
                order, created=Order.objects.get_or_create(customer=customer,complete=False)
                items=order.orderitem_set.all()
                flag=True      
                item_count=Wishlist.get_total_WishlistItems()
                no_items=OrderItem.get_total_orderItems(request.user)
                  
                available_offers={}
                for item in items:
                    available_offers[item]=[]
                offer_discount=0
                greatestoffer=None
                for item in items:
                    if item.product.offer:
                        available_offers[item].append(item.product.offer)
                    if item.product.category.offer:
                        available_offers[item].append(item.product.category.offer)
                    if item.product.brand.first().offer:
                        available_offers[item].append(item.product.brand.first().offer)
                if available_offers:
                    for item,offers in available_offers.items():
                        for offer in offers:
                            if offer.discount>offer_discount:
                                offer_discount=offer.discount
                                greatestoffer=offer
                   
        else:

            return redirect('/accounts/logout')
    else:

        cookieData=Cookie_cart(request)
        items=cookieData['items']
        order=cookieData['order']
        no_items=cookieData['no_items']
        item_count=cookieData['item_count']
        address=[]
        
        context={
            'items':items,
            'order':order,
            'no_items':no_items,
            'flag':flag,
            'address':address,
            'item_count':item_count,
            
        }
        
        
        if 'add' in request.session:

            add= request.session['add']
            add['uid']=uuid.UUID(add['uid'])
            address.append(add)
            context['address']=address
        else:
            messages.warning(request,"add address to continue !!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if not items:
            messages.warning(request,"Your cart is empty, cartify some !!")
            return redirect('/')
        
        name=add['first_name']+add['last_name']
        email=add['email']
        customer, created=Customer.objects.get_or_create(
            email=email
        )
        customer.name=name
        customer.save()

        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        address=Address.objects.create(
            first_name=add['first_name'],
            last_name=add['last_name'],
            email=add['email'],
            phone=add['phone'],
            address=add['address'],
            city=add['city'],
            state=add['state'],
            country=add['country'],
            pincode=add['pincode'],
            is_default=True
        )
        order.shipping_address=address
        order.save()
        for item in items:
            product=Products.objects.get(uid=item['product']['uid'])
            product_variant=ProductVariant.objects.get(uid=item['uid'])
            orderitem,created=OrderItem.objects.get_or_create(
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
    context={
        'items':items,
        'order':order,
        'no_items':no_items,
        'flag':flag,
        }
    if not request.user.is_authenticated:
        context['no_items']=cookieData['no_items']
        item_count=0
    else:
        context['offer']=greatestoffer

            
    context['item_count']=item_count
    
    
    form=PaymentForm(initial={'payment_method': order.payment_method})
    context['form']=form
    return render(request,'checkout/payment.html',context)
def razorpaycheck(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                customer=request.user.customer
                
        else:
            return redirect('/accounts/logout')
    else:
        if 'add' in request.session:
            add= request.session['add']
        name=add['first_name']+add['last_name']
        email=add['email']
        customer=Customer.objects.get(email=email,name=name)
    order, created=Order.objects.get_or_create(customer=customer,complete=False)
    items=order.orderitem_set.all()
    total_price=order.get_grand_total
    customer_name=customer.name
    customer_email=customer.email
    phone=order.shipping_address.phone
    return JsonResponse({
        'total_price':total_price,
        'customer_name':customer_name,
        'customer_email':customer_email,
        'phone':phone,
    })
def payment_method(request):
    flag=False
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone=data.get('phone')
        payment_method = data.get('paymentMethod')
        try:
            if request.user.is_authenticated and not request.user.is_superuser:
                if request.user.is_otp_verified:
                    if request.user.is_blocked:
                        messages.warning(request,"Account Blocked !!")
                        return redirect('/accounts/logout')
                    else:
                        customer=request.user.customer
                        flag=True      
                        tem_count=Wishlist.get_total_WishlistItems()
                        
                else:
                    return redirect('/accounts/logout')
            else:
                customer=Customer.objects.get(email=email,name=name)

            order=Order.objects.get(customer=customer,complete=False)
            items=order.orderitem_set.all()
            total_price=order.get_grand_total
            order.payment_method=payment_method
            if order.payment_method=='Paypal':
                
                return JsonResponse({'redirect': '/checkout/paypal-payment/'})
            if order.payment_method==payment_method:
                order.complete=True
                order.status='processed'
                now = timezone.localtime().now()
                order.date_ordered=now
                order.delivery_date=now+timedelta(weeks=1)
                for item in items:
                    item.ordered=True
                    product_variant=item.product_variant
                    product_variant.quantity=product_variant.quantity-item.quantity
                    product_variant.save()
                    item.save()
                transaction_id='ORDER'+str(random.randint(11111,99999))
                while Order.objects.filter(transaction_id=transaction_id) is None:
                    transaction_id='ORDER'+str(random.randint(11111,99999))
                order.transaction_id=transaction_id
                order.save()
                response = JsonResponse({
                    'success': True, 
                    'message': 'Order Placed'
                })

                response.delete_cookie('cart')

                return response
                
            else:
            
                return JsonResponse({
                'success': False, 'message': 'Cannot be placed'
            })
            
        except Order.DoesNotExist:
            return HttpResponse(status=404)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
def paypal_method(request):
    flag=False
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone=data.get('phone')
        payment_method = data.get('paymentMethod')
        try:
            if request.user.is_authenticated and not request.user.is_superuser:
                if request.user.is_otp_verified:
                    if request.user.is_blocked:
                        messages.warning(request,"Account Blocked !!")
                        return redirect('/accounts/logout')
                    else:
                        customer=request.user.customer
                        flag=True      
                        tem_count=Wishlist.get_total_WishlistItems()
                        
                else:
                    return redirect('/accounts/logout')
            else:
                customer=Customer.objects.get(email=email,name=name)

            order=Order.objects.get(customer=customer,complete=False)
            items=order.orderitem_set.all()
            total_price=order.get_grand_total
            order.payment_method=payment_method
            if order.payment_method=='Paypal':
                order.complete=True
                order.status='processed'
                now = timezone.localtime().now()
                order.date_ordered=now
                order.delivery_date=now+timedelta(weeks=1)
                for item in items:
                    item.ordered=True
                    product_variant=item.product_variant
                    product_variant.quantity=product_variant.quantity-item.quantity
                    product_variant.save()
                    item.save()
                transaction_id='ORDER'+str(random.randint(11111,99999))
                while Order.objects.filter(transaction_id=transaction_id) is None:
                    transaction_id='ORDER'+str(random.randint(11111,99999))
                order.transaction_id=transaction_id
                order.save()
                response = JsonResponse({
                    'success': True, 
                    'message': 'Order Placed'
                })

                response.delete_cookie('cart')

                return response
                
            else:
            
                return JsonResponse({
                'success': False, 'message': 'Cannot be placed'
            })
            
        except Order.DoesNotExist:
            return HttpResponse(status=404)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
def paypal_payment(request):
    flag=False
    context={}
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                customer=request.user.customer
                order=Order.objects.get(customer=customer,complete=False)
                items=order.orderitem_set.all()
                flag=True      
                item_count=Wishlist.get_total_WishlistItems()
                available_offers={}
                for item in items:
                    available_offers[item]=[]
                offer_discount=0
                greatestoffer=None
                no_items=OrderItem.get_total_orderItems(request.user)
                for item in items:
                    if item.product.offer:
                        available_offers[item].append(item.product.offer)
                    if item.product.category.offer:
                        available_offers[item].append(item.product.category.offer)
                    if item.product.brand.first().offer:
                        available_offers[item].append(item.product.brand.first().offer)
                if available_offers:
                    for item,offers in available_offers.items():
                        for offer in offers:
                            if offer.discount>offer_discount:
                                offer_discount=offer.discount
                                greatestoffer=offer
                   
        else:

            return redirect('/accounts/logout')
    else:

        cookieData=Cookie_cart(request)
        items=cookieData['items']
        order=cookieData['order']
        no_items=cookieData['no_items']
        item_count=cookieData['item_count']
        address=[]
        
        context={
            'items':items,
            'order':order,
            'no_items':no_items,
            'flag':flag,
            'address':address,
            'item_count':item_count,
            
        }
        
        
        if 'add' in request.session:

            add= request.session['add']
            add['uid']=uuid.UUID(add['uid'])
            address.append(add)
            context['address']=address
        else:
            messages.warning(request,"add address to continue !!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if not items:
            messages.warning(request,"Your cart is empty, cartify some !!")
            return redirect('/')
        
        name=add['first_name']+add['last_name']
        email=add['email']
        customer=Customer.objects.get(
            email=email,name=name
        )
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        address=order.shipping_address
        items=order.orderitem_set.all()
    context={
        'items':items,
        'order':order,
        'no_items':no_items,
        'flag':flag,
        }
    if not request.user.is_authenticated:
        context['no_items']=cookieData['no_items']
        item_count=0

    else:
        context['offer']=greatestoffer
        


            
    context['item_count']=item_count
    return render(request,'checkout/onlinepayment.html',context)