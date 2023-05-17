from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
from .models import *
from cart.models import OrderItem
from product.models import *
from django.template.loader import render_to_string
from django.db.models import Min, Max
import json
from wishlist.models import *
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import ReviewForm


# Create your views here.
def products_details(request, slug):
    try:
        product=Products.objects.get(slug=slug,status=1)
        related_products=Products.objects.filter(category=product.category).exclude(uid=product.uid)[:3]
        flag=False
        no_items=0
        item_count=0
        if request.user.is_superuser:
            return redirect('/accounts/logout')
        if  request.user.is_authenticated:
            if request.user.is_otp_verified: 
                
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()

                flag=True
        else:
            try:
                cart=json.loads(request.COOKIES['cart'])
            except:
                cart={}
            no_items=len(cart)
            item_count=0
        
        context = {
                'product':product,
                "flag" : flag,
                "no_items":no_items,
                'related_products':related_products,
                'section_slug': product.section.first().slug, 
                
                }
        reviews_on_product=Review.objects.filter(product=product).order_by('-added_at')
        reviews_count=Review.objects.filter(product=product).count()
        if  request.user.is_authenticated: 
            review_by_user=Review.objects.filter(product=product,user=request.user)
            context['review_by_user']=review_by_user

        context['item_count']=item_count
        context['reviews_on_product']=reviews_on_product
        context['reviews_count']=reviews_count
        context['itrator']=range(1,6)
        print('avg rating:-----------',Review.get_average_rating(product))
        rating=Review.get_average_rating(product)
        if rating:
            avarage_rating = round(Review.get_average_rating(product), 1)
            context['avarage_rating']=avarage_rating
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.product=product
                review.save()
                previous_page = request.META.get('HTTP_REFERER')
                return HttpResponseRedirect(previous_page)
        else:
            form = ReviewForm()
            context['form']=form
    
        
        colors=ProductVariant.objects.filter(product=product).values('color__name','color__uid').distinct()
        sizes=ProductVariant.objects.filter(product=product).values('size__name','size__uid','color__uid','extra_price','quantity').distinct()
        by_age=ProductVariant.objects.filter(product=product).values('by_age__name','by_age__uid','color__uid','extra_price','quantity').distinct()
        firstcolor=colors[0]['color__name']
        print('size',sizes[0]['size__name'])
        print('color',firstcolor)
        print('product',product)
        print(product.section.first().name)
        if product.section.first().name=='Kids':
            variant=ProductVariant.objects.filter(product=product,color__name=firstcolor,by_age__name=by_age[0]['by_age__name'])[0]

        else:
            if ProductVariant.objects.filter(product=product,color__name=firstcolor,size__name=sizes[0]['size__name'])[0]:
                variant=ProductVariant.objects.filter(product=product,color__name=firstcolor,size__name=sizes[0]['size__name'])[0]
            else:
                print('list is scene')
        context['colors']=colors
        context['default_quantity']=variant.quantity
        context['sizes']=sizes
        context['by_age']=by_age
        context['selling_price']=product.selling_price
        updated_price=product.selling_price
        if request.GET.get('size'):
            size=request.GET.get('size')
            print(size)
            extra_price=product.get_product_price_by_variants(size)
            print('manipulated price = ',extra_price)
            context['selected_size'] = size
            updated_price = updated_price+extra_price
        if request.GET.get('color'):
            color=request.GET.get('color')
            print(color)
            context['selected_color']=color
            extra_price=product.get_extra_price_by_color(color)
            updated_price = updated_price+extra_price
        context['updated_price']=updated_price
        available_offer=[]
        if product.offer:
            available_offer.append(product.offer)
        if product.category.offer:
            available_offer.append(product.category.offer)
        if product.brand.first().offer:
            available_offer.append(product.brand.first().offer)
        offer_discount=0
        greatestoffer=None
        if available_offer:
            for offer in available_offer:
                if offer.discount>offer_discount:
                    offer_discount=offer.discount
                    greatestoffer=offer
        context['offer']=greatestoffer
        return render(request, 'products/products.html',context)
        
    except Exception as e:
        print(e)
    

def group_view(request,slug):
    try:
        flag=False
        no_items=0
        if request.user.is_superuser:
            return redirect('/accounts/logout')
        if  request.user.is_authenticated:
            no_items=OrderItem.get_total_orderItems(request.user)
            item_count=Wishlist.get_total_WishlistItems()
            flag=True
        else:
            try:
                cart=json.loads(request.COOKIES['cart'])
            except:
                cart={}
            no_items=len(cart) 
            item_count=0
    
        if(Section.objects.filter(slug=slug)):
            all_groups=Section.objects.all()
            products_list=Products.objects.filter(section__slug=slug,status=1)
            all_categories=Category.objects.all()
            all_products=Products.objects.filter(status=1)
            all_colors=Color.objects.all()
            all_sizes=Size.objects.all().exclude(name='None')
            all_ages=By_Age.objects.all().exclude(name='None')
            all_brands=Brand.objects.all()
            min_max_price=Products.objects.aggregate(Min('selling_price'),Max('selling_price'))
            categories_women=[]
            women_product=Products.objects.filter(section__slug='women')
            women_category=[]
            for product in women_product:
                category=product.category
                if category not in women_category:
                    women_category.append(category)
            men_product=Products.objects.filter(section__slug='men')
            men_category=[]
            for product in men_product:
                category=product.category
                if category not in men_category:
                    men_category.append(category)
            kids_product=Products.objects.filter(section__slug='kids')
            kids_category=[]
            for product in kids_product:
                category=product.category
                if category not in kids_category:
                    kids_category.append(category)

            group=Section.objects.filter(slug=slug)
        paginator = Paginator(products_list, 12) 
        page = request.GET.get('page')
        products = paginator.get_page(page)   
        context={
                'products': products,
                "flag" : flag,
                'group':group,
                'all_groups':all_groups,
                'no_items':no_items,
                'women_category':women_category,
                'men_category':men_category,
                'kids_category':kids_category,
                'all_colors':all_colors,
                'all_sizes':all_sizes,
                'all_ages':all_ages,
                'all_categories':all_categories,
                'all_brands':all_brands,
                'min_max_price':min_max_price,
                'slug':slug,
                }
        context['item_count']=item_count
        avarage_rating={}
        for product in products:
            rating=Review.get_average_rating(product)
            if rating:
                avarage_rating[product.uid] = round(Review.get_average_rating(product), 1)
        context['avarage_rating']=avarage_rating
        return render(request, 'products/product_shop.html',context)
        
        
    except Exception as e:
        print(e)
    return render(request, 'products/product_shop.html')
    
def cateogory_view(request,name):
    
    try:
        flag=False
        no_items=0
        if request.user.is_superuser:
            return redirect('/accounts/logout')
        if  request.user.is_authenticated:
            if request.user.is_otp_verified:
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()
                flag=True
        else:
            try:
                cart=json.loads(request.COOKIES['cart'])
            except:
                cart={}
            no_items=len(cart)
            item_count=0
        try:
            if Category.objects.get(name=name):
                
                category=Category.objects.get(name=name)
                products=Products.objects.filter(category=category,status=1)
                all_groups=Section.objects.all()
                all_colors=Color.objects.all()
                all_sizes=Size.objects.all().exclude(name='None')
                all_ages=By_Age.objects.all().exclude(name='None')
                all_categories=Category.objects.all()
                all_brands=Brand.objects.all()
                min_max_price=Products.objects.aggregate(Min('selling_price'),Max('selling_price'))
                
                categories_women=[]
                women_product=Products.objects.filter(section__slug='women')
                women_category=[]
                for product in women_product:
                    category=product.category
                    if category not in women_category:
                        women_category.append(category)
                men_product=Products.objects.filter(section__slug='men')
                men_category=[]
                for product in men_product:
                    category=product.category
                    if category not in men_category:
                        men_category.append(category)
                kids_product=Products.objects.filter(section__slug='kids')
                kids_category=[]
                for product in kids_product:
                    category=product.category
                    if category not in kids_category:
                        kids_category.append(category)
                context={
                    'products': products,
                    "flag" : flag,
                    'category':category,
                    'all_groups':all_groups,
                    'no_items':no_items,
                    'women_category':women_category,
                    'men_category':men_category,
                    'kids_category':kids_category,
                    'all_colors':all_colors,
                    'all_sizes':all_sizes,
                    'all_ages':all_ages,
                    'all_categories':all_categories,
                    'all_brands':all_brands,
                    'min_max_price':min_max_price,

                    }
        except:
            products=Products.objects.filter(meta_keywords__icontains=name)
            all_groups=Section.objects.all()
            all_colors=Color.objects.all()
            all_sizes=Size.objects.all().exclude(name='None')
            all_ages=By_Age.objects.all().exclude(name='None')
            all_categories=Category.objects.all()
            all_brands=Brand.objects.all()
            min_max_price=Products.objects.aggregate(Min('selling_price'),Max('selling_price'))
            
            categories_women=[]
            women_product=Products.objects.filter(section__slug='women')
            women_category=[]
            for product in women_product:
                category=product.category
                if category not in women_category:
                    women_category.append(category)
            men_product=Products.objects.filter(section__slug='men')
            men_category=[]
            for product in men_product:
                category=product.category
                if category not in men_category:
                    men_category.append(category)
            kids_product=Products.objects.filter(section__slug='kids')
            kids_category=[]
            for product in kids_product:
                category=product.category
                if category not in kids_category:
                    kids_category.append(category)
            context={
                'products': products,
                "flag" : flag,
                'all_groups':all_groups,
                'no_items':no_items,
                'women_category':women_category,
                'men_category':men_category,
                'kids_category':kids_category,
                'all_colors':all_colors,
                'all_sizes':all_sizes,
                'all_ages':all_ages,
                'all_categories':all_categories,
                'all_brands':all_brands,
                'min_max_price':min_max_price,
                }
        context['item_count']=item_count
        context['slug']=name
        avarage_rating={}
        for product in products:
            rating=Review.get_average_rating(product)
            if rating:
                avarage_rating[product.uid] = round(Review.get_average_rating(product), 1)
        context['avarage_rating']=avarage_rating

        return render(request, 'products/categories_shop.html',context)
    except Exception as e:
        
        print(e)
    return render(request, 'products/categories_shop.html',context)

def shop(request):
    try:
        flag=False
        no_items=0
        if request.user.is_superuser:
            return redirect('/accounts/logout')
        if  request.user.is_authenticated:
            if request.user.is_otp_verified:
                no_items=OrderItem.get_total_orderItems(request.user)
                item_count=Wishlist.get_total_WishlistItems()
                flag=True
        else:
            try:
                cart=json.loads(request.COOKIES['cart'])
            except:
                cart={}
            no_items=len(cart)
            item_count=0
        if Products.objects.all():
            all_groups=Section.objects.all()
            products_list=Products.objects.filter(status=1)
            all_categories=Category.objects.all()
            all_products=Products.objects.filter(status=1)
            all_colors=Color.objects.all()
            all_sizes=Size.objects.all().exclude(name='None')
            all_ages=By_Age.objects.all().exclude(name='None')
            all_brands=Brand.objects.all()
            min_max_price=Products.objects.aggregate(Min('selling_price'),Max('selling_price'))
            categories_women=[]
            women_product=Products.objects.filter(section__slug='women')
            women_category=[]
            for product in women_product:
                category=product.category
                if category not in women_category:
                    women_category.append(category)
            men_product=Products.objects.filter(section__slug='men')
            men_category=[]
            for product in men_product:
                category=product.category
                if category not in men_category:
                    men_category.append(category)
            kids_product=Products.objects.filter(section__slug='kids')
            kids_category=[]
            for product in kids_product:
                category=product.category
                if category not in kids_category:
                    kids_category.append(category)

            group=Section.objects.all()
        paginator = Paginator(products_list, 6) 
        page = request.GET.get('page')
        products = paginator.get_page(page)   
        context={
                'products': products,
                "flag" : flag,
                'group':group,
                'all_groups':all_groups,
                'no_items':no_items,
                'women_category':women_category,
                'men_category':men_category,
                'kids_category':kids_category,
                'all_colors':all_colors,
                'all_sizes':all_sizes,
                'all_ages':all_ages,
                'all_categories':all_categories,
                'all_brands':all_brands,
                'min_max_price':min_max_price,
                'slug':None,
                }
        context['item_count']=item_count
        avarage_rating={}
        for product in products:
            rating=Review.get_average_rating(product)
            if rating:
                avarage_rating[product.uid] = round(Review.get_average_rating(product), 1)
        context['avarage_rating']=avarage_rating
        return render(request, 'products/product_shop.html',context)
        
        
    except Exception as e:
        print(e)
    return render(request, 'products/product_shop.html')

def filter_data(request):
    colors=request.GET.getlist('color[]')
    categories=request.GET.getlist('category[]')
    brands=request.GET.getlist('brand[]')
    sizes=request.GET.getlist('size[]')
    ages=request.GET.getlist('by_age[]')
    min=request.GET['_minPrice']
    max=request.GET['maxPrice']
    slug=request.GET['slug']
    allProducts=Products.objects.filter(status=1).distinct()
    if slug=='None':
        allProducts=Products.objects.filter(status=1).distinct()

    elif slug=='women':
        allProducts=Products.objects.filter(status=1,section__slug=slug).distinct()
    elif slug=='men':
        allProducts=Products.objects.filter(status=1,section__slug=slug).distinct()
    elif slug=='kids':
        allProducts=Products.objects.filter(status=1,section__slug=slug).distinct()
    else:
        try:
            if Category.objects.get(name=slug):
                category=Category.objects.get(name=slug)
                allProducts=Products.objects.filter(category=category,status=1)
        except:
            allProducts=Products.objects.filter(meta_keywords__icontains=slug)


    allProducts=allProducts.filter(selling_price__gte=min) 
    allProducts=allProducts.filter(selling_price__lte=max)
    if len(colors)>0:
        allProducts=allProducts.filter(product_variant__color__uid__in=colors).distinct()
    if len(categories)>0:
        allProducts=allProducts.filter(category__uid__in=categories).distinct()
    if len(brands)>0:
        allProducts=allProducts.filter(brand__uid__in=brands).distinct()
    if len(sizes)>0:
        allProducts=allProducts.filter(product_variant__size__uid__in=sizes).distinct()
    if len(ages)>0:
        allProducts=allProducts.filter(product_variant__by_age__uid__in=ages).distinct()
    avarage_rating={}
    for product in allProducts:
        rating=Review.get_average_rating(product)
        if rating:
            avarage_rating[product.uid] = round(Review.get_average_rating(product), 1)
    t=render_to_string('base/product_list.html',{'data':allProducts,'avarage_rating':avarage_rating})
    
    return JsonResponse({'data':t})
    
def sort_data(request):
    option=request.GET['selectedOption']
    print('option---------------------',option)
    slug=request.GET['slug']
    allProducts=Products.objects.filter(status=1).distinct()
    if slug=='None':
        allProducts=Products.objects.filter(status=1).distinct()
    elif slug=='women':
        allProducts=Products.objects.filter(status=1,section__slug=slug).distinct()
    elif slug=='men':
        allProducts=Products.objects.filter(status=1,section__slug=slug).distinct()
    elif slug=='kids':
        allProducts=Products.objects.filter(status=1,section__slug=slug).distinct()
    else:
        try:
            if Category.objects.get(name=slug):
                category=Category.objects.get(name=slug)
                allProducts=Products.objects.filter(category=category,status=1)
        except:
            allProducts=Products.objects.filter(meta_keywords__icontains=slug)
    if option==None or option=='prce-asc':
        allProducts=allProducts.order_by('selling_price')
    elif option=='prce-desc':
        allProducts=allProducts.order_by('-selling_price')
    elif option=='newn':
        allProducts=allProducts.order_by('-created_at')
    elif option=='relevance':
        allProducts=allProducts.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
    
    avarage_rating={}
    for product in allProducts:
        rating=Review.get_average_rating(product)
        if rating:
            avarage_rating[product.uid] = round(Review.get_average_rating(product), 1)
    
    
    t=render_to_string('base/product_list.html',{'data':allProducts,'avarage_rating':avarage_rating})
    return JsonResponse({'data':t})
 

def product_list(request):
    product_keyword=Products.objects.filter(status=1).values_list('meta_keywords',flat=True)
    categories=Category.objects.filter(status=1).values_list('name',flat=True)
    klist=list(product_keyword)
    clist=list(categories)
    first_list = []
    second_list=[]
    for string in klist:
        first_list.extend(string.split(","))
    for string in clist:
        second_list.extend(string.split(","))
    merged_list = first_list + second_list
    set_list=set(merged_list)
    final_list=list(set_list)
    return JsonResponse(final_list,safe=False)

def searchproduct(request):
    if request.method=='POST':
        searchkey=request.POST.get('searchkey')
        if searchkey=="":
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            category=Category.objects.filter(name=searchkey)
            if category:
                return redirect('products/category_filter/'+searchkey)
            
            product=Products.objects.filter(meta_keywords__icontains=searchkey)
            if product:
                return redirect('products/category_filter/'+searchkey)
            else:
                messages.warning(request,"No such products !!")
                return redirect(request.META.get('HTTP_REFERER'))
                
    return redirect(request.META.get('HTTP_REFERER'))

    
    
    
    
    
    
    
   