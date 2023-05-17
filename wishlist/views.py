from django.shortcuts import render,redirect
from cart.models import *
from .models import *
import json
from django.contrib import messages
from django.http import  Http404,HttpResponse,HttpResponseRedirect,JsonResponse
from django.core.paginator import Paginator

# Create your views here.

def view_wishlist(request):
    context={}
    flag=False
    if request.user.is_superuser:
        return redirect('/accounts/logout')
    if request.user.is_authenticated:
        flag=True
        context['flag']=flag
        no_items=OrderItem.get_total_orderItems(request.user)
        context['no_items']=no_items
        item_count=Wishlist.get_total_WishlistItems()
        context['item_count']=item_count

        if Wishlist.objects.filter(user=request.user):
            wishitem_list=Wishlist.objects.filter(user=request.user)
            paginator = Paginator(wishitem_list, 6) 
            page = request.GET.get('page')
            wishitem = paginator.get_page(page)
            context['wishitem']=wishitem
            
            
        else:
          context['message']='Your Wishlist is Empty'
    else:
        return redirect('/accounts/login')
    return render(request,'wishlist/index.html',context)

def add_to_wishlist(request):
    data=json.loads(request.body)
    product_uid=data['uid']
    if request.user.is_superuser:
        return redirect('/accounts/logout')
    if request.user.is_authenticated:
        if Products.objects.get(uid=product_uid):
            product=Products.objects.get(uid=product_uid)
            if Wishlist.objects.filter(user=request.user,product=product):
                return JsonResponse('Product already exist in wishlist', safe=False)
            else:
                wishitem=Wishlist.objects.create(user=request.user,product=product)
                return JsonResponse('product added to favorites',safe=False)
        else:
            return JsonResponse('No such product available',safe=False)
    else:
        return JsonResponse('You need to login for this',safe=False)

    
def delete_from_wishlist(request):
    data=json.loads(request.body)
    product_uid=data['uid']
    if request.user.is_superuser:
        return redirect('/accounts/logout')
    if request.user.is_authenticated:
        if Products.objects.get(uid=product_uid):
            product=Products.objects.get(uid=product_uid)
            if Wishlist.objects.filter(user=request.user,product=product):
                Wishlist.objects.filter(user=request.user,product=product).delete()
                return JsonResponse('Product removed from wishlist', safe=False)
            else:
                return JsonResponse('Product not found in wishlist', safe=False)

        else:
            return JsonResponse('No such product available',safe=False)
    else:
        return redirect('/accounts/login')
        


