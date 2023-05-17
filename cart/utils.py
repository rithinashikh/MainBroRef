from .models import *
from product.models import *
import json

def Cookie_cart(request):
    try:
        cart=json.loads(request.COOKIES['cart'])
    except:
        cart={}
    print('cart',cart,len(cart))

    items=[]
    order={'get_cart_total':0,'get_cart_items':0}
    no_items=0
    no_items=len(cart)
    item_count=0

    for i in cart:
        try:
            product=Products.objects.get(uid=cart[i]['uid'])
            color=Color.objects.get(uid=cart[i]['color'])
            is_kids_section = product.section.filter(name="Kids").exists()

            if is_kids_section:

                section='Kids'
                size=By_Age.objects.get(name=cart[i]['size'])
                product_variant=ProductVariant.objects.filter(product=product,by_age=size,color=color)[0]

            else:
                section='other'
                size=Size.objects.get(name=cart[i]['size'])
                product_variant=ProductVariant.objects.filter(product=product,size=size,color=color)[0]
            get_price=(product.selling_price+product_variant.extra_price)
            get_total=get_price*cart[i]['quantity']
            order['get_cart_total']+=get_total
            order['get_cart_items']+=cart[i]["quantity"]
            order['get_discount']=0
            order['get_grand_total']=order['get_cart_total']+order['get_discount']

            item={
                'product':{
                'uid':product.uid,
                'name':product.name,
                'product_images':{
                    'first':{
                        'img':product.product_images.first().img
                    },
                },
                'section.first.name':section,
                },
                'product_variant':{
                    
                    'by_age':{
                        'name':size.name
                    },
                    'size':{
                        'name':size.name
                    },
                    'color':{
                        'name':color.name,
                        'uid':color.uid,
                    },
                'quantity':product_variant.quantity, 
                },
                'quantity':cart[i]['quantity'],
                'get_total':get_total,
                'get_price':get_price,
                'uid':product_variant.uid,
                    
                    
            }
            items.append(item)
        except:
            pass
    return {'items':items,
            'order':order,
            'no_items':no_items,
            'item_count':item_count,}

def Cart_address(request):
    
    first_name=request.POST.get('first_name')
    last_name=request.POST.get('last_name')
    country=request.POST.get('country')
    address=request.POST.get('address')
    city=request.POST.get('city')
    state=request.POST.get('state')
    pincode=request.POST.get('pincode')
        
    phone=request.POST.get('phone')
    email=request.POST.get('email')
    is_default=True
    uid=uuid.uuid4()

            
    add={
        'first_name':first_name,
        'last_name':last_name,
        'email':email,
        'phone':phone,
        'address':address,
        'city':city,
        'state':state,
        'country':country,
        'pincode':pincode,
        'is_default':is_default,
        'uid':str(uid),
    }
    
    return add