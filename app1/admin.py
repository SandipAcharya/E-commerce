from django.contrib import admin
from .models import Profile, Vendor,Category,Image, Product, ProductVariant


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','phone_number','address','created_at']

admin.site.register(Profile,ProfileAdmin)

class VendorAdmin(admin.ModelAdmin):
    list_display = ['user','store_name',
                    'subscription_plan','subscription_expiry','created_at','updated_at']

admin.site.register(Vendor,VendorAdmin)


class CategoryAdmin(admin.ModelAdmin):
  list_display = ['name', 'parent']
admin.site.register(Category,CategoryAdmin)

class ImageAdmin(admin.ModelAdmin):
   list_display =['image_name']

admin.site.register(Image,ImageAdmin)

class ProductAdmin(admin.ModelAdmin):
   list_display = ['name','vendor','price','category','stock','created_at','updated_at']

admin.site.register(Product,ProductAdmin)


class ProductVariantAdmin(admin.ModelAdmin):
   list_display=['name','value','stock']
admin.site.register(ProductVariant, ProductVariantAdmin)

# havenot register other cause  need to change them in to professional look