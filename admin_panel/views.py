from django.shortcuts import render,HttpResponse,redirect
from accounts.models import User
from product.models import *
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from admin_panel.forms import *
from django.contrib import messages
import random
from accounts.forms import CustomUserForm
from cart.models import *
from django.http import  Http404,HttpResponse,HttpResponseRedirect,JsonResponse
import json
from .models import *
from datetime import datetime, timedelta
from django.utils import timezone
import datetime
from django.db.models import Count
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.
# _________________________________________________admin_____________________________________________
@never_cache
def adminlogin(request):
    
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('/admin-panel/')
    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=authenticate(request,email=email,password=password)
        if user is not None:
            if user.is_superuser:
                login(request,user)
                return redirect('/admin-panel/')
            else:
                messages.warning(request,"Incorrect Credentials !!")
    form = signinuserForm()        

    return render(request,'admin_panel/login.html',{'form':form})

@never_cache
def adminpage(request):
    if request.user.is_authenticated and request.user.is_superuser:
        users=User.objects.all()
        admin=User.objects.get(is_superuser=True)
        total_income=0
        total_orders=0
        orders=Order.objects.filter(complete=True)
        total_products=Products.objects.filter(status=1).count()
        total_registrations=User.objects.filter(is_superuser=False).count()
        income_orders=orders.exclude(status__in=['returned', 'canceled', 'refunded'])
        
        
        for order in orders:
            total_orders+=1
        for order in income_orders:
            total_income+=order.get_grand_total
        total_income=round(total_income,2)
        today = timezone.localtime().now()
        this_week = today - datetime.timedelta(days=7)
    
        this_month = today.replace(day=1)
        this_year = today.replace(month=1, day=1)
        num_weeks = ((today - this_month).days + 6) // 7 


        orders_delivered = Order.objects.filter(
        date_ordered__range=[this_week, today],
        complete=True,status='delivered',
        ).values('transaction_id','date_ordered')
        orders_placed = Order.objects.filter(
        date_ordered__range=[this_week, today],
        complete=True
        ).values('transaction_id','date_ordered')
        weekly_count={}
        weekly_delivered={}
        for i in orders_placed:
            ordered_date=i['date_ordered'].date()
            if ordered_date in weekly_count:
                weekly_count[ordered_date]+=1
            else:
                weekly_count[ordered_date]=1
        for i in orders_delivered:
            ordered_date=i['date_ordered'].date()
            if ordered_date in weekly_delivered:
                weekly_delivered[ordered_date]+=1
            else:
                weekly_delivered[ordered_date]=1

        # _____________________________________________Monthly Report___________________________________________

        orders_delivered_monthly = Order.objects.filter(
            date_ordered__range=[this_month, today],
            complete=True,
            status='delivered'
        ).values('transaction_id','date_ordered')

        orders_placed_monthly = Order.objects.filter(
            date_ordered__range=[this_month, today],
            complete=True
        ).values('transaction_id','date_ordered')

       
        monthly_count = {f"Week {i+1}": 0 for i in range(num_weeks)}
        monthly_delivered = {f"Week {i+1}": 0 for i in range(num_weeks)}
       
        for order in orders_placed_monthly:
            ordered_date = order['date_ordered'].date()
            week_num = (ordered_date.day - 1) // 7  # calculate which week 
            monthly_count[f"Week {week_num+1}"] += 1
        for order in orders_delivered_monthly:
            ordered_date = order['date_ordered'].date()
            week_num = (ordered_date.day - 1) // 7  # calculate which week the order is in
            monthly_delivered[f"Week {week_num+1}"] += 1
        
# _____________________________________________Yearly Report___________________________________________
        orders_delivered_yearly = Order.objects.filter(
            date_ordered__range=[this_year, today],
            complete=True,
            status='delivered'
        ).values('transaction_id','date_ordered')

        orders_placed_yearly = Order.objects.filter(
            date_ordered__range=[this_year, today],
            complete=True
        ).values('transaction_id','date_ordered')

        months={
            1:'January',
            2:'February',
            3:'March',
            4:'April',
            5:'May',
            6:'June',
            7:'July',
            8:'August',
            9:'September',
            10:'October',
            11:'November',
            12:'December',
        }
        yearly_count = {months[i]: 0 for i in range(1, 13)}
        yearly_delivered = {months[i]: 0 for i in range(1, 13)}
        
        for order in orders_placed_yearly:
            ordered_date = order['date_ordered']
            month_num = ordered_date.month
            month=months[month_num]
            yearly_count[month] +=1
            
        for order in orders_delivered_yearly:
            ordered_date = order['date_ordered']
            month_num = ordered_date.month
            month=months[month_num]
            yearly_delivered[month] +=1
         # _____________________________________for pie diagram___________________________
        products=Products.objects.filter(status=1)
        products_count={'Men':0,'Women':0,'Kids':0}
        for product in products:
            if product.section.first().name=='Kids':
                products_count['Kids']+=1
            elif product.section.first().name=='Women':
                products_count['Women']+=1
            elif product.section.first().name=='Men':
                products_count['Men']+=1
        # _____________________________________for Bardiagram___________________________________
        #_______________week_________________________
        daily_orders = Order.objects.filter(
        date_ordered__range=[this_week, today],
        complete=True
        ).exclude(status__in=['returned','refunded','canceled'])
        daily_income={}
        for order in daily_orders:
            ordered_date=order.date_ordered.date()
            if ordered_date in daily_income:
                daily_income[ordered_date]+=order.get_grand_total
            else:
                daily_income[ordered_date]=order.get_grand_total

        #____________________month__________________________   
        monthly_orders = Order.objects.filter(
            date_ordered__range=[this_month, today],
            complete=True
        ).exclude(status__in=['returned','refunded','canceled'])
        monthly_income = {f"Week {i+1}": 0 for i in range(num_weeks)}
        for order in monthly_orders:
            ordered_date = order.date_ordered.date()
            week_num = (ordered_date.day - 1) // 7  # calculate which week 
            monthly_income[f"Week {week_num+1}"] += order.get_grand_total
        #_______________________________yearly________________________________
        yearly_orders = Order.objects.filter(
            date_ordered__range=[this_year, today],
            complete=True
        ).exclude(status__in=['returned','refunded','canceled'])
        yearly_income = {months[i]: 0 for i in range(1, 13)}
        for order in yearly_orders:
            ordered_date = order.date_ordered.date()
            month_num = ordered_date.month
            month=months[month_num]
            yearly_income[month] +=order.get_grand_total
        #_______________________________New Products______________________________________
        new_products = Products.objects.filter(status=1).order_by('-created_at')[:5]
        all_orders=Order.objects.filter(complete=True)

        ordered_products={}
        for order in all_orders:
            items=order.orderitem_set.all()
            for item in items:
                item=item.product
                if item in ordered_products:
                    ordered_products[item]+=1
                else:
                    ordered_products[item]=1
        top_selling_products= dict(sorted(ordered_products.items(), key=lambda item: item[1],reverse=True))  
        top_selling_products=dict(list(top_selling_products.items())[:5])
        variants=ProductVariant.objects.all()
        product_qty={}
        for var in variants:
            for product in products:
                if var.product==product:
                    if product in product_qty and product_qty[product]>var.quantity:
                        product_qty[product]=var.quantity
                    elif product not in product_qty:
                        product_qty[product]=var.quantity
        soon_to_be_outoforder = dict(sorted(product_qty.items(), key=lambda item: item[1])).items()
        soon_to_be_outoforder=dict(list(soon_to_be_outoforder)[:5])

        for product in products:
            if product not in ordered_products:
                ordered_products[product]=0
        least_selling_products= dict(sorted(ordered_products.items(), key=lambda item: item[1])).items()  
        least_selling_products=dict(list(least_selling_products)[:5])
        #_______________________________New Orders______________________________

        new_orders=Order.objects.filter(complete=True).order_by('-date_ordered')[:5]
        
        # _________________________________end______________________________________________________________

        details={'users':users,
                'admin':admin,
                'total_income':total_income,
                'total_orders':total_orders, 
                'total_products':total_products,
                'total_registrations':total_registrations,
                'weekly_count':weekly_count,
                'weekly_delivered':weekly_delivered,
                'monthly_delivered':monthly_delivered,
                'monthly_count':monthly_count,
                'yearly_count':yearly_count,
                'yearly_delivered':yearly_delivered,
                'products_count':products_count,
                'daily_income':daily_income,
                'monthly_income':monthly_income,
                'yearly_income':yearly_income,
                'top_selling_products':top_selling_products,
                'soon_to_be_outoforder':soon_to_be_outoforder,
                'least_selling_products':least_selling_products,
                'new_orders':new_orders,
                 }
        return render(request,'admin_panel/dashboard.html',details)
    else:
        return redirect('/admin-panel/login')
def customer_details(request):
    if request.user.is_authenticated and  request.user.is_superuser:
        users_list=User.objects.filter(is_superuser=False).order_by('-date_joined')
        searchkey=request.GET.get('searchkey')
        if searchkey:
            if searchkey!="":
                if User.objects.filter(first_name__icontains=searchkey):
                    users_list=users.filter(first_name__icontains=searchkey)
                else:
                    messages.warning(request,"No customers found !!")
                    users_list=User.objects.filter(is_superuser=False).order_by('-date_joined')

            else:
                users_list=User.objects.filter(is_superuser=False).order_by('-date_joined')
        paginator = Paginator(users_list, 5) 
        page = request.GET.get('page')
        users = paginator.get_page(page)
        admin=request.user
        details={'users':users,
                 'admin':admin,
                 
                 }
        return render(request,'admin_panel/customers.html',details)
    else:
        return redirect('/admin-panel/login')

def adminlogout(request):
    logout(request)
    return redirect('/admin-panel/login')
# _________________________________________________customer_____________________________________________

def Customer_delete(request,id):
    
    User.objects.get(id=id).delete()
    messages.success(request,"User Deleted !!")
    return redirect('/admin-panel/customers')
        
def customer_update(request,id):
    user=User.objects.get(id=id)
    admin=User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = CustomUpdateForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            
            return redirect('/admin-panel/customers')
    else:
        form = CustomUpdateForm(instance=user) 

    
    return render(request,'admin_panel/customer_update.html',{'form':form,'admin':admin})

def add_customer(request):
    admin=User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        
        if form.is_valid():
            form.save()
            
            return redirect('/admin-panel/customers')
    else:
        form = CustomUserForm()
    return render(request,'admin_panel/add_customer.html',{'form':form,'admin':admin})
# _________________________________________________product__________________________________________
def product_details(request):
    if request.user.is_authenticated and request.user.is_superuser:
        products_list=Products.objects.all().order_by('-created_at')
        admin=User.objects.get(is_superuser=True)
        searchkey=request.GET.get('searchkey')
        if searchkey:
            if searchkey!="":
                if products_list.filter(name=searchkey):
                    products_list=products_list.filter(name__icontains=searchkey)
                elif Category.objects.filter(name__icontains=searchkey):
                    category=Category.objects.filter(name__icontains=searchkey)
                    products_list=products_list.filter(category__in=category)
                else:
                    messages.warning(request,"No such products !!")
                    products_list=Products.objects.all().order_by('-created_at')
            else:
               products_list=Products.objects.all().order_by('-created_at') 
        paginator = Paginator(products_list, 5) 
        page = request.GET.get('page')
        products = paginator.get_page(page)
        details={'products':products,
                 'admin':admin,
        }
        return render(request,'admin_panel/products.html',details)
    else:
        return redirect('/admin-panel/login')

def product_delete(request,uid):
    Products.objects.get(uid=uid).delete()
    messages.success(request,"Product Deleted !!")
    return redirect('/admin-panel/products')

def product_update(request,uid):
    products=Products.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        product_form = ProductUpdateForm(request.POST, instance=products)
        image_form=ProductImageFormSet(request.POST, request.FILES,instance=product_form.instance)
        variant_form=ProductVariantFormSet(request.POST,request.FILES,instance=product_form.instance)
        
        if product_form.is_valid() and image_form.is_valid() and variant_form.is_valid():
            product_form.save()
            image_form.save()
            variant_form.save()
            return redirect('/admin-panel/products')
        
        return HttpResponse('form is not valid')
    else:
        product_form = ProductUpdateForm(instance=products)
        image_form=ProductImageFormSet(instance=products)
        variant_form=ProductVariantFormSet(instance=products)
        context={
            'form':product_form,
            'admin':admin,
            'image_form':image_form,
            'variant_form':variant_form,
            }
    
        return render(request,'admin_panel/product_update.html',context)

def add_product(request):
    admin=User.objects.get(is_superuser=True)
    # ProductUpdateformset = inlineformset_factory(Products, ProductImage, form=ProductImageForm, extra=4, can_delete=True)
    ProductVariantFormSet = inlineformset_factory(
        Products, ProductVariant, form=ProductVariantForm, extra=4, can_delete=True
    )
    ProductImageFormSet = inlineformset_factory(
        Products, ProductImage, form=ProductImageForm, extra=4, can_delete=True
    )
    if request.method == 'POST':
        product_form = ProductUpdateForm(request.POST)
        image_form=ProductImageFormSet(request.POST,request.FILES,instance=product_form.instance)
        variant_form=ProductVariantFormSet(request.POST,request.FILES,instance=product_form.instance)

        if product_form.is_valid() and image_form.is_valid() and variant_form.is_valid():
            product_form.save()
            image_form.save()
            variant_form.save()
            return redirect('/admin-panel/products')
        else:
            context = {'form': product_form, 'form_data': request.POST}
            context={
            'form':product_form,
            'admin':admin,
            'image_form':image_form,
            'form_data': request.POST,
            'variant_form':variant_form,
            }
        return render(request,'admin_panel/add_product.html',context)
    else:
        product_form = ProductUpdateForm()
        image_form=ProductImageFormSet(instance=product_form.instance)
        variant_form=ProductVariantFormSet(instance=product_form.instance)
        context={
            'form':product_form,
            'admin':admin,
            'image_form':image_form,
            'variant_form':variant_form,
            }
    return render(request,'admin_panel/add_product.html',context)

# -------------------------------------------------variant------------------------------------------------
def variant_details(request):
    if request.user.is_authenticated and  request.user.is_superuser:
        brands=Brand.objects.all()
        colors=Color.objects.all()
        sizes=Size.objects.all()
        by_age=By_Age.objects.all()
        tags=Tags.objects.all()
        admin=User.objects.get(is_superuser=True)
        
        context={'brands':brands,
                 'admin':admin,
                 'colors':colors,
                 'sizes':sizes,
                 'by_age':by_age,
                 'tags':tags,
                 
                 }
        return render(request,'admin_panel/variants.html',context)
    else:
        return redirect('/admin-panel/login')
# _________________________________________brands_______________________________________________
def add_brands(request):
    admin=User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = BrandUpdationForm(request.POST,request.FILES)
        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/variants')
        else:
            print('form not valid')
    else:
        form = BrandUpdationForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_brand.html',context)

def brand_update(request,uid):
    brand=Brand.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = BrandUpdationForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('/admin-panel/variants')
    else:
        form = BrandUpdationForm(instance=brand)
        context={
            'form':form,
            'admin':admin,
            }
        return render(request,'admin_panel/add_brand.html',context)

def brand_delete(request,uid):
    Brand.objects.get(uid=uid).delete()
    messages.success(request,"brand Deleted !!")
    return redirect('/admin-panel/variants')
# _________________________________________Colors_______________________________________________
def add_color(request):
    admin=User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = ColorUpdationForm(request.POST,request.FILES)
        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/variants')
        else:
            print('form not valid')
    else:
        form = ColorUpdationForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_color.html',context)

def color_update(request,uid):
    color=Color.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = ColorUpdationForm(request.POST, request.FILES, instance=color)
        if form.is_valid():
            form.save()
            return redirect('/admin-panel/variants')
    else:
        form = ColorUpdationForm(instance=color)
        context={
            'form':form,
            'admin':admin,
            }
        return render(request,'admin_panel/add_color.html',context)

def color_delete(request,uid):
    Color.objects.get(uid=uid).delete()
    messages.success(request,"color Deleted !!")
    return redirect('/admin-panel/variants')
# _________________________________________Sizes_______________________________________________
def add_size(request):
    admin=User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = SizeUpdationForm(request.POST,request.FILES)
        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/variants')
        else:
            print('form not valid')
    else:
        form = SizeUpdationForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_size.html',context)

def size_update(request,uid):
    size=Size.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = SizeUpdationForm(request.POST, request.FILES, instance=size)
        if form.is_valid():
            form.save()
            return redirect('/admin-panel/variants')
    else:
        form = SizeUpdationForm(instance=size)
        context={
            'form':form,
            'admin':admin,
            }
        return render(request,'admin_panel/add_size.html',context)

def size_delete(request,uid):
    Size.objects.get(uid=uid).delete()
    messages.success(request,"size Deleted !!")
    return redirect('/admin-panel/variants')
# _________________________________________by_age_______________________________________________
def add_age(request):
    admin=User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = AgeUpdationForm(request.POST,request.FILES)
        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/variants')
        else:
            print('form not valid')
    else:
        form = AgeUpdationForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_age.html',context)

def age_update(request,uid):
    by_age=By_Age.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = AgeUpdationForm(request.POST, request.FILES, instance=by_age)
        if form.is_valid():
            form.save()
            return redirect('/admin-panel/variants')
    else:
        form = AgeUpdationForm(instance=by_age)
        context={
            'form':form,
            'admin':admin,
            }
        return render(request,'admin_panel/add_age.html',context)

def age_delete(request,uid):
    By_Age.objects.get(uid=uid).delete()
    messages.success(request,"Age variant Deleted !!")
    return redirect('/admin-panel/variants')
# 
# _________________________________________tag_______________________________________________
def add_tag(request):
    admin=User.objects.get(is_superuser=True)
    if request.method == 'POST':
        form = TagUpdationForm(request.POST,request.FILES)
        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/variants')
        else:
            print('form not valid')
    else:
        form = TagUpdationForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_tag.html',context)

def tag_update(request,uid):
    tag=Tags.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = TagUpdationForm(request.POST, request.FILES, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('/admin-panel/variants')
    else:
        form = TagUpdationForm(instance=tag)
        context={
            'form':form,
            'admin':admin,
            }
        return render(request,'admin_panel/add_tag.html',context)

def tag_delete(request,uid):
    Tags.objects.get(uid=uid).delete()
    messages.success(request,"tag Deleted !!")
    return redirect('/admin-panel/variants')
# 

#_____________________________________________sections and sub-sections_____________________________
#     
def Sections_details(request):
    if request.user.is_authenticated and  request.user.is_superuser:
        sections=Section.objects.all()
        sub_sections=Sub_groups.objects.all()
        
        admin=User.objects.get(is_superuser=True)
        context={'sections':sections,
                 'admin':admin,
                 'sub_sections':sub_sections,
                
                 }
        return render(request,'admin_panel/sections.html',context)
    else:
        return redirect('/admin-panel/login')

def add_sections(request):
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = SectionUpdateForm(request.POST,request.FILES)

        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/sections')
        else:
            print('form not valid')
    else:
        form = SectionUpdateForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_section.html',context)

def section_update(request,uid):
    section=Section.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = SectionUpdateForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            return redirect('/admin-panel/sections')
    else:
        form = SectionUpdateForm(instance=section)
        context={
            'form':form,
            'admin':admin,
            'image_form':form,
            }
        return render(request,'admin_panel/add_section.html',context)

def section_delete(request,uid):
    Section.objects.get(uid=uid).delete()
    messages.success(request,"Section Deleted !!")
    return redirect('/admin-panel/sections')
# ___________________________________________________________________________///////////////////
def add_subsections(request):
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = SubsectionUpdateForm(request.POST,request.FILES)

        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/sections')
        else:
            print('form not valid')
    else:
        form = SubsectionUpdateForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_subsection.html',context)

def subsection_update(request,uid):
    subsection=Sub_groups.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = SubsectionUpdateForm(request.POST, request.FILES, instance=subsection)
        if form.is_valid():
            form.save()
            return redirect('/admin-panel/sections')
    else:
        form = SubsectionUpdateForm(instance=subsection)
        context={
            'form':form,
            'admin':admin,
            'image_form':form,
            }
        return render(request,'admin_panel/add_subsection.html',context)

def subsection_delete(request,uid):
    Sub_groups.objects.get(uid=uid).delete()
    messages.success(request,"Sub-section Deleted !!")
    return redirect('/admin-panel/sections')
#__________________________Categories_____________________________________

def Category_details(request):
    if request.user.is_authenticated and  request.user.is_superuser:
        categories_list=Category.objects.all()
        searchkey=request.GET.get('searchkey')
        if searchkey:
            if searchkey!="":
                if Category.objects.filter(name__icontains=searchkey):
                    categories_list=categories.filter(name__icontains=searchkey)
                else:
                    messages.warning(request,"No customers found !!")
                    categories_list=Category.objects.all()

            else:
                categories_list=Category.objects.all()
        paginator = Paginator(categories_list, 5) 
        page = request.GET.get('page')
        categories = paginator.get_page(page)
        admin=User.objects.get(is_superuser=True)
        context={'categories':categories,
                 'admin':admin,
                
                 }
        return render(request,'admin_panel/categories.html',context)
    else:
        return redirect('/admin-panel/login')

def add_category(request):
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST,request.FILES)

        if form.is_valid() :
            form.save()    
            return redirect('/admin-panel/categories')
        else:
            print('form not valid')
    else:
        form = CategoryUpdateForm()
    context= {
            'form':form,
            'admin':admin, 
            }
    return render(request,'admin_panel/add_category.html',context)

def category_update(request,uid):
    categories=Category.objects.get(uid=uid)
    admin=User.objects.get(is_superuser=True)

    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST,request.FILES, instance=categories)
        
        if form.is_valid():
            form.save()
            
            return redirect('/admin-panel/categories')
    else:
        form = CategoryUpdateForm(instance=categories)
        context={
            'form':form,
            'admin':admin,
            'image_form':form
            }
    
    return render(request,'admin_panel/add_category.html',context)

def Category_delete(request,uid):
    Category.objects.get(uid=uid).delete()
    messages.success(request,"Category Deleted !!")
    return redirect('/admin-panel/categories')

#____________________________________Orders___________________________________________

def view_all_orders(request):
    if request.user.is_authenticated and  request.user.is_superuser:
        admin=request.user
        context={}
        context['admin']=admin
        if Order.objects.filter(complete=True):
            orders_list=Order.objects.filter(complete=True).order_by('-date_ordered')
            from_date=request.GET.get('from_date')
            to_date=request.GET.get('to_date')
            if from_date and to_date:
                orders_list = orders.filter(date_ordered__gte=from_date, date_ordered__lte=to_date)
            paginator = Paginator(orders_list, 5) 
            page = request.GET.get('page')
            orders = paginator.get_page(page)
            context['orders']=orders
            return render(request,'admin_panel/orders.html',context)
        else:
            messages.warning(request,"No order summary !!")
            return render(request,'admin_panel/orders.html',context)
                    
    else:
        return redirect('/admin-panel/logout')
def update_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_uid = data.get('orderUId')
        delivery_date = data.get('deliveryDate')
        status = data.get('status')
       
        try:
            order = Order.objects.get(uid=order_uid)
            order.delivery_date = delivery_date
            order.status = status
            order.save()
            return JsonResponse('order updated',safe=False)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': f'Order with UId {order_uid} not found'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def view_order_details(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        context={}
        admin=request.user
        context['admin']=admin
        if Order.objects.get(complete=True,uid=uid):
            order=Order.objects.get(complete=True,uid=uid)
            items=order.orderitem_set.all()
            context['order']=order
            context['items']=items
            return render(request,'admin_panel/order_details.html',context)
        else:
            messages.warning(request,"No order summary !!")
            return render(request,'orders/summary.html',context)
                    
        
    else:
        return redirect('/admin-panel/logout')

#__________________________________coupons_______________________________________________
def Coupon_details(request):
    if request.user.is_authenticated and  request.user.is_superuser:
        coupons_list=Coupon.objects.all()
        searchkey=request.GET.get('searchkey')
        if searchkey:
            if searchkey!="":
                if Coupon.objects.filter(coupon_code__icontains=searchkey):
                    coupons_list=coupons.filter(coupon_code__icontains=searchkey)
                else:
                    messages.warning(request,"No coupons found !!")
                    coupons_list=Coupon.objects.all()

            else:
                coupons_list=Coupon.objects.all()
        paginator = Paginator(coupons_list, 5) 
        page = request.GET.get('page')
        coupons = paginator.get_page(page)
        admin=User.objects.get(is_superuser=True)
        context={'coupons':coupons,
                 'admin':admin,
                
                 }
        if request.method == 'POST':
            form = AddCoupon(request.POST,request.FILES)

            if form.is_valid() :
                form.save()    
                return redirect('/admin-panel/coupons')
            
        else:
            form = AddCoupon()
            context['form']=form
        return render(request,'admin_panel/coupons.html',context)
    else:
        return redirect('/admin-panel/login')

def coupon_delete(request,uid):
    Coupon.objects.get(uid=uid).delete()
    messages.success(request,"Coupon Deleted !!")
    return redirect('/admin-panel/coupons')

def update_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        couponuid = data.get('couponuid')
        couponCode = data.get('couponCode')
        description = data.get('description')
        discountPrice = data.get('discountPrice')
        minimumAmount = data.get('minimumAmount')
        isExpired = data.get('isExpired')
       
        try:
            coupon = Coupon.objects.get(uid=couponuid)
            coupon.coupon_code=couponCode
            coupon.description=description
            coupon.discount_price=discountPrice
            coupon.minimum_amount=minimumAmount
            coupon.is_expired=isExpired
            coupon.save()
            return JsonResponse('coupon updated',safe=False)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': f'{couponCode} not found'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
# ______________________________________admin_profile_________________________________________________
def admin_profile(request):
    if request.user.is_authenticated and request.user.is_superuser:
        admin=request.user
        flag=True
        context={
            'admin':admin,

        }
        if request.method == 'POST':
            profile_form = profileUpdate(request.POST, instance=admin)
            if profile_form.is_valid():
                profile_form.save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            profile_form = profileUpdate(instance=admin)
            context['profile_form']=profile_form
        return render(request,'admin_panel/personal_info.html',context)
        
    else:
        return redirect('/admin-panel/login')

def update_admin_profile(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            request.user.image = image
            request.user.save()
            return JsonResponse({'image': request.user.image.url})
    return JsonResponse({'error': 'Invalid request'})

def View_BankDetails(request):
    if request.user.is_authenticated and request.user.is_superuser:
        admin=request.user
        account_details=Admin_Bank_Details.objects.filter(admin=request.user)
        context={
            'admin':admin,
            'account_details':account_details,
        }
        return render(request,'admin_panel/bank_accounts.html',context)
    else:
        return redirect('/admin-panel/login')

def add_account_details(request):
    context={}
    if request.user.is_authenticated and request.user.is_superuser:
        admin=request.user
        context['admin']=admin
        if request.method == 'POST':
            form = Bank_details(request.POST)
            if form.is_valid():
                account = form.save(commit=False)
                account.admin = request.user  # Assign the current user to the address
                account.save()
                return redirect('/admin-panel/admin-bank-details')
            else:
                # Render the same form page with the invalid form data
                context ['form']= form
                context['form_data']=request.POST
                
                return render(request, 'admin_panel/add_bank_details.html', context)
        else:
            form = Bank_details()
            context['form']=form
        return render(request,'admin_panel/add_bank_details.html',context)
    else:
        return redirect('/admin-panel/login')

def edit_account_details(request,uid):
    context={}
    if request.user.is_authenticated and request.user.is_superuser:
        admin=request.user
        context['admin']=admin
        account=Admin_Bank_Details.objects.get(uid=uid)
        if request.method == 'POST':
            form = Bank_details(request.POST, instance=account)
            if form.is_valid():
                form.save()
                return redirect('/admin-panel/admin-bank-details')
        else:
            form = Bank_details(instance=account)
            context['form']=form
        return render(request,'admin_panel/add_bank_details.html',context)
    else:
        return redirect('/admin-panel/login')


def delete_account(request,uid):
    Admin_Bank_Details.objects.get(uid=uid).delete()
    messages.success(request,"Account Deleted !!")
    return redirect('/admin-panel/admin-bank-details')

def security(request):
    if request.user.is_authenticated and request.user.is_superuser:
                admin=request.user
                context={
                    'admin':admin,
                }
                try:
                    if request.method == 'POST':
                        current_password=request.POST.get('current_password')
                        new_password=request.POST.get('new_pass1')
                        confirm_password=request.POST.get('new_pass2')
                        if admin.check_password(current_password):
                            if new_password != confirm_password:
                                messages.warning(request,'Passwords are not equal')
                                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                            else:
                                admin.set_password(new_password)
                                admin.save()
                                messages.success(request,'Password changed')
                        else:
                            messages.warning(request,"Incorrect password !!")
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                except Exception as e:
                    print(e)
                
                return render(request,'admin_panel/admin_security.html',context)
       
    else:
        return redirect('/admin-panel/login')

#______________________________________sales Report_________________________________
def sales_report(request):
    admin=request.user
    orders_list=Order.objects.filter(complete=True).order_by('-date_ordered')
    from_date=request.GET.get('from_date')
    to_date=request.GET.get('to_date')
    if from_date and to_date:
        orders_list = orders_list.filter(date_ordered__gte=from_date, date_ordered__lte=to_date)
    paginator = Paginator(orders_list, 10) 
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    total_orders=orders_list.count()
    net_income=0
    net_cart=0
    income_orderlist=orders_list.exclude(status__in=['returned', 'canceled', 'refunded'])
    for order in income_orderlist:
        net_cart+=order.get_original_cart_total
        net_income+=order.get_grand_total
    net_discount=net_cart-net_income
    deliveries=orders_list.filter(status='delivered').count()
    canceled=orders_list.filter(Q(status='canceled') | Q(status='returned')).count()
    pending=orders_list.filter(status='pending').count()
    context={
        'admin':admin,
        'orders':orders,
        'total_orders':total_orders,
        'net_income':net_income,
        'net_discount':net_discount,
        'net_cart':net_cart,
        'deliveries':deliveries,
        'canceled':canceled,
        'pending':pending,
    }
    return render(request,'admin_panel/salesreport.html',context) 


# -------------------------------------------------------------------------------------------
# __________________________searching___________________________________________________
# _______________****products********________________________________________________
def admin_panel_products(request):
    product_keyword=Products.objects.filter(status=1).values_list('name',flat=True)
    categories=Category.objects.filter(status=1).values_list('name',flat=True)
    klist=list(product_keyword)
    clist=list(categories)
    merged_list = klist + clist
    set_list=set(merged_list)
    final_list=list(set_list)
    return JsonResponse(final_list,safe=False)

def admin_panel_customers(request):
    customers=User.objects.filter(is_superuser=False).values_list('first_name',flat=True)
    customer_list=list(customers)
    return JsonResponse(customer_list,safe=False)

def coupons_list_admin(request):
    coupons=Coupon.objects.all().values_list('coupon_code',flat=True)
    coupon_list=list(coupons)
    return JsonResponse(coupon_list,safe=False)
def category_list_admin(request):
    category=Category.objects.all().values_list('name',flat=True)
    category_list=list(category)
    return JsonResponse(category_list,safe=False)
def offers_list_admin(request):
    offers=Offer.objects.all().values_list('name',flat=True)
    offers_list=list(offers)
    return JsonResponse(offers_list,safe=False)
            
#__________________________________offers_______________________________________________
def Offer_details(request):
    if request.user.is_authenticated and  request.user.is_superuser:
        offers_list=Offer.objects.all()
        searchkey=request.GET.get('searchkey')
        if searchkey:
            if searchkey!="":
                if Offer.objects.filter(name__icontains=searchkey):
                    offers_list=offers_list.filter(name__icontains=searchkey)
                else:
                    messages.warning(request,"No such offers found !!")
                    offers_list=Offer.objects.all()

            else:
                offers_list=Offer.objects.all()
        paginator = Paginator(offers_list, 5) 
        page = request.GET.get('page')
        offers = paginator.get_page(page)
        admin=User.objects.get(is_superuser=True)
        context={'offers':offers,
                 'admin':admin,
                
                 }
        if request.method == 'POST':
            form = AddOffer(request.POST,request.FILES)

            if form.is_valid() :
                form.save()    
                return redirect('/admin-panel/offers')
            
        else:
            form = AddOffer()
            context['form']=form
        return render(request,'admin_panel/offer.html',context)
    else:
        return redirect('/admin-panel/login')

def offer_delete(request,uid):
    Offer.objects.get(uid=uid).delete()
    messages.success(request,"Offer Deleted !!")
    return redirect('/admin-panel/offers')

def update_offer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        offeruid = data.get('offeruid')
        offername = data.get('offername')
        discount = data.get('discount')
        status = data.get('active')
       
        try:
            offer = Offer.objects.get(uid=offeruid)
            offer.name=offername
            offer.discount=discount
            offer.active=status
            offer.save()
            return JsonResponse('offer updated',safe=False)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': f'{offername} not found'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
# _