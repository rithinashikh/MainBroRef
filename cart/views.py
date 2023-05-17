
from django.http import JsonResponse, Http404,HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect,render
from django.contrib import messages
from product.models import *
from .models import *
from accounts.models import User
import json
from .forms import *
from .utils import Cookie_cart
from wishlist.models import Wishlist
from django.core.paginator import Paginator

def cartpage(request):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.method=='POST':
        if request.user.is_authenticated and not request.user.is_superuser:
            coupon=request.POST.get('coupon')
            if Coupon.objects.filter(coupon_code__icontains=coupon):
                coupon_obj=Coupon.objects.get(coupon_code__icontains=coupon)
                if coupon_obj.is_expired:
                    messages.warning(request,"Coupon expired !!")
                    
                else:
                    customer,created=Customer.objects.get_or_create(user=request.user)
                    order, created=Order.objects.get_or_create(customer=customer,complete=False)
                    if order.coupon:
                        messages.warning(request,"Coupon already exist !!")
                    else:
                        if 'firstbuy' in coupon_obj.coupon_code:
                            if Order.objects.filter(customer=customer,complete=True):
                                messages.warning(request,"Coupon only applicable for first purchase, try another !!")
                            else:
                                if order.get_cart_total>coupon_obj.minimum_amount:
                                    order.coupon=coupon_obj
                                    order.save()
                                    messages.warning(request,"Coupon applied !!")
                                else:
                                    messages.warning(request,"Coupon is not applicable for the current bag amount !!")

                        else:
                            if order.get_cart_total>coupon_obj.minimum_amount:
                                order.coupon=coupon_obj
                                order.save()
                                messages.warning(request,"Coupon applied !!")
                            else:
                                messages.warning(request,"Coupon is not applicable for the current bag amount !!")
            else:
                messages.warning(request,"Coupon dont exist !!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            return redirect('accounts/login')
    if request.user.is_authenticated and not request.user.is_superuser:
        if request.user.is_otp_verified:
            if request.user.is_blocked:
                messages.warning(request,"Account Blocked !!")
                return redirect('/accounts/logout')
            else:
                customer,created=Customer.objects.get_or_create(user=request.user)
                order, created=Order.objects.get_or_create(customer=customer,complete=False)
                order.set_defaultaddress()
                order.save()
                print('shipping address :',order.shipping_address)
                if order.coupon:
                    if order.get_cart_total<order.coupon.minimum_amount:
                        order.coupon=None
                        order.save()
                items_list=order.orderitem_set.all()
                no_items=OrderItem.get_total_orderItems(request.user)
                paginator = Paginator(items_list, 5) 
                page = request.GET.get('page')
                items = paginator.get_page(page)

                context={
                    'items':items,
                    'order':order,
                    'no_items':no_items
                }
                flag=True
                context['flag']=flag
                available_coupons=Coupon.objects.filter(is_expired=False)
                context['available_coupons']=available_coupons
                item_count=Wishlist.get_total_WishlistItems()
                context['item_count']=item_count 
                available_offers={}
                for item in items:
                    available_offers[item]=None                
                for item in items:
                    if item.product.offer:
                        if not available_offers[item] or available_offers[item].discount<item.product.offer.discount:
                            available_offers[item]=item.product.offer
                    if item.product.category.offer:
                        if not available_offers[item] or available_offers[item].discount<item.product.category.offer.discount:
                            available_offers[item]=item.product.category.offer
                    if item.product.brand.first().offer:
                        if not available_offers[item] or available_offers[item].discount<item.product.brand.first().offer.discount:
                            available_offers[item]=item.product.brand.first().offer
                context['offer']=available_offers 
                
                return render(request,'cart/cart.html',context)
                
    else:
        cookieData=Cookie_cart(request)
        items=cookieData['items']
        order=cookieData['order']
        no_items=cookieData['no_items']
        item_count=cookieData['item_count']
        flag=False
        context={
            'items':items,
            'order':order,
            'no_items':no_items,
            'item_count':item_count,
        }
        print(context)
        context['flag']=flag
    return render(request,'cart/cart.html',context)

def add_to_cart(request):
    data=json.loads(request.body)
    product_uid=data['uid']
    qty=int(data['qty'])
    action=data['action']
    selected_color=data['selected_color']
    selected_size=data['selected_size']
    print('selected size is ',selected_size)
    if request.user.is_authenticated:
        customer,created=Customer.objects.get_or_create(user=request.user)
        if Products.objects.get(uid=product_uid):
            product=Products.objects.get(uid=product_uid)
            color=Color.objects.get(uid=selected_color)
            is_kids_section = product.section.filter(name="Kids").exists()
        
            if is_kids_section:
                size=By_Age.objects.get(name=selected_size)
                product_variant=ProductVariant.objects.get(product=product,color=color,by_age=size)
                
            else:
                size=Size.objects.get(name=selected_size)
                product_variant=ProductVariant.objects.get(product=product,color=color,size=size)
            if qty>product_variant.quantity:
                return JsonResponse('Only'+' '+str(product_variant.quantity)+' '+'is available',safe=False)
            else:
                order, created=Order.objects.get_or_create(customer=customer,complete=False)
                order.set_defaultaddress()
                order.save()
                print('shipping address :',order.shipping_address)
                orderItem, created= OrderItem.objects.get_or_create(product=product,product_variant=product_variant,order=order)
                if action=='add':
                    orderItem.quantity=(orderItem.quantity+qty)
                    if orderItem.quantity>product_variant.quantity:
                        orderItem.quantity=(orderItem.quantity-qty)
                        return JsonResponse('Only'+' '+str(product_variant.quantity-orderItem.quantity)+' '+' is available',safe=False)
                elif action=='up':
                    if orderItem.quantity==product_variant.quantity:
                        return JsonResponse('Not enough quantity',safe=False)
                    else:
                        orderItem.quantity=(orderItem.quantity+1)
                elif action=='down':
                    orderItem.quantity=(orderItem.quantity-1)
                orderItem.save() 
                
                if orderItem.quantity <=0:
                    orderItem.delete()
                return JsonResponse('Cart Updated', safe=False)
                   
        else:
            return JsonResponse('No such product available',safe=False)
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0}
        no_items=0
        context={
            'items':items,
            'order':order,
            'no_items':no_items
        }
        
        return render(request,'cart/cart.html',context)
        

def product_delete(request,uid):
    if request.user.is_superuser:
         return redirect('/accounts/logout')
    if request.user.is_authenticated and not request.user.is_superuser:
        order=Order.objects.get(complete=False,customer__user=request.user)
        
        OrderItem.objects.get(uid=uid).delete()
        if not OrderItem.objects.all():
            order.delete()
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        try:
            cart=json.loads(request.COOKIES['cart'])
        except:
            cart={}
        product_variant=ProductVariant.objects.get(uid=uid)
        key_size=str(product_variant.product.uid)+'-'+str(product_variant.color.uid)+'-'+str(product_variant.size.name)

        if key_size in cart:
           del cart[key_size]
        
        response.set_cookie('cart', json.dumps(cart))
        if not cart:
            response.delete_cookie('cart')
            messages.success(request, 'Product Deleted !!')
    return response


def remove_coupon(request,uid):
    order=Order.objects.get(uid=uid)
    order.coupon=None
    order.save()
    messages.warning(request,"Coupon removed !!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_offer(request):
    data=json.loads(request.body)
    offer_name=data['offerName']
    itemId=data['itemId']
    offer=Offer.objects.get(name=offer_name)
    item=OrderItem.objects.get(order__customer__user=request.user,uid=itemId)
    item.offer=offer
    item.is_offer_applied=True
    item.save()
    return JsonResponse('offer added'+itemId+offer_name,safe=False)