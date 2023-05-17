from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(Coupon)
class ProductImageInline(admin.StackedInline):
    model=ProductImage

class ProductVariantInline(admin.StackedInline):
    model=ProductVariant


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display=['name','selling_price']
    inlines=[ProductImageInline,ProductVariantInline]


# admin.site.register(Images_product)
# admin.site.register(Products, ProductsAdmin)

admin.site.register(Section)
admin.site.register(Brand)
admin.site.register(Sub_groups)
admin.site.register(Offer)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['user','product']
    model=Review
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display=['name']
    model=Color

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display=['name']
    model=Size

@admin.register(By_Age)
class By_AgeAdmin(admin.ModelAdmin):
    list_display=['name']
    model=By_Age

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    model=Tags
