from django.shortcuts import render,redirect
from cart.models import *
from django.contrib import messages
from django.http import  Http404,HttpResponse,HttpResponseRedirect,JsonResponse
from product.models import *
from datetime import datetime, timedelta
from cart.utils import Cookie_cart
from wishlist.models import *
from django.core.paginator import Paginator



# Create your views here.

def view_orders(request):
    context={}
    flag=False
    item_count=0
    if request.user.is_superuser:
         return redirect('/accounts/logout')
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
        if 'add' in request.session:
            customer=Customer.objects.get(email=request.session['add']['email'])
            cookieData=Cookie_cart(request)
            context['no_items']=cookieData['no_items']
        else:
            messages.warning(request,"No existing Orders")
            return redirect('/')
    if Order.objects.filter(customer=customer,complete=True):
        orders_list=Order.objects.filter(customer=customer,complete=True).order_by('-date_ordered')
        paginator = Paginator(orders_list, 5) 
        page = request.GET.get('page')
        orders = paginator.get_page(page)
        context['orders']=orders
        context['flag']=flag
        context['item_count']=item_count
        return render(request,'orders/orderlist.html',context)
    else:
        messages.warning(request,"No order summary !!")
        
            
    return render(request,'orders/orderlist.html',context)
    
                    
def order_summary(request,uid):
    context={}
    flag=False
    item_count=0
    if request.user.is_superuser:
         return redirect('/accounts/logout')
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
        customer=Customer.objects.get(email=request.session['add']['email'])
        cookieData=Cookie_cart(request)
        context['no_items']=cookieData['no_items']
    if Order.objects.get(customer=customer,complete=True,uid=uid):
        order=Order.objects.get(customer=customer,complete=True,uid=uid)
        items=order.orderitem_set.all()
        context['order']=order
        context['items']=items
        context['item_count']=item_count

        context['flag']=flag
        return render(request,'orders/summary.html',context)
    else:
        messages.warning(request,"No order summary !!")
        return render(request,'orders/summary.html',context)
                    
def cancel_order(request,uid):
    context={}
    item_count=0
    if request.user.is_superuser:
         return redirect('/accounts/logout')
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

        else:
                return redirect('/accounts/logout')
    else:
        customer=Customer.objects.get(email=request.session['add']['email'])
        cookieData=Cookie_cart(request)
        context['no_items']=cookieData['no_items']
    if Order.objects.get(customer=customer,complete=True,uid=uid):
        order=Order.objects.get(customer=customer,complete=True,uid=uid)
        if order.status != 'canceled':
            order.status='canceled'
            now = timezone.localtime().now()
            order.canceled_date=now
            items=order.orderitem_set.all()
            for item in items:
                product_variant=item.product_variant
                product_variant.quantity=product_variant.quantity+item.quantity
                product_variant.save()
                order.save()
            messages.success(request,"Order canceled")
            return redirect('/order')
                    
        else:
            messages.warning(request,"No order summary !!")
            return redirect('/order')
                    
    
#_____________________________return order_______________________________________
def return_order(request,uid):
    context={}
    item_count=0
    if request.user.is_superuser:
         return redirect('/accounts/logout')
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
        else:
            return redirect('/accounts/logout')
    else:
        customer=Customer.objects.get(email=request.session['add']['email'])
        cookieData=Cookie_cart(request)
        context['no_items']=cookieData['no_items']
    if Order.objects.get(customer=customer,complete=True,uid=uid):
        order=Order.objects.get(customer=customer,complete=True,uid=uid)
        if order.status != 'returned':
            order.status='returned'
            now = timezone.localtime().now()
            order.returned_date=now
            items=order.orderitem_set.all()
            for item in items:
                product_variant=item.product_variant
                product_variant.quantity=product_variant.quantity+item.quantity
                product_variant.save()
            order.save()
            messages.success(request,"return requested")
    else:
        messages.warning(request,"No order summary !!")
    return redirect('/order')
                    