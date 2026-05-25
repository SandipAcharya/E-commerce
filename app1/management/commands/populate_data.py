import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from app1.models import Category, Product, Vendor, Image, Profile, ProductVariant
from userapp.models import CustomerUser
from allauth.account.models import EmailAddress
from django.core.files.base import ContentFile
import urllib.parse
import os
import random

class Command(BaseCommand):
    help = 'Populates the database with realistic products, profiles, and variants'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cleaning up old generated data...')
        Category.objects.all().delete()
        
        target_email = 'acharyasandip137@gmail.com'
        target_phone = '9861403964'

        self.stdout.write('Creating realistic users, vendors, and profiles...')
        
        # Create normal users & Profiles
        for name in ['michael', 'sarah', 'david']:
            user, _ = CustomerUser.objects.get_or_create(username=name, defaults={'email': target_email, 'is_vendor': False})
            user.set_password('password123')
            user.save()
            Profile.objects.get_or_create(user=user, defaults={'phone_number': target_phone, 'address': '123 E-Commerce St, Kathmandu'})
            EmailAddress.objects.get_or_create(user=user, email=target_email, defaults={'primary': True, 'verified': True})

        # Create Vendors & Profile
        vendor_user, _ = CustomerUser.objects.get_or_create(username='tech_vendor', defaults={'is_vendor': True, 'email': target_email})
        vendor_user.set_password('password123')
        vendor_user.save()
        Profile.objects.get_or_create(user=vendor_user, defaults={'phone_number': target_phone, 'address': 'Tech Hub HQ'})
        EmailAddress.objects.get_or_create(user=vendor_user, email=target_email, defaults={'primary': True, 'verified': True})
        
        vendor, _ = Vendor.objects.get_or_create(user=vendor_user, defaults={'store_name': 'Tech Hub', 'description': 'Premium electronics store'})

        self.stdout.write('Fetching data from FakeStoreAPI...')
        try:
            response = requests.get('https://fakestoreapi.com/products')
            response.raise_for_status()
            products_data = response.json()
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch data: {e}'))
            return

        for item in products_data:
            # Handle Category
            cat_name = item['category'].title()
            category, _ = Category.objects.get_or_create(name=cat_name, slug=slugify(cat_name))

            # Create Product
            product, p_created = Product.objects.get_or_create(
                vendor=vendor,
                name=item['title'],
                defaults={
                    'description': item['description'],
                    'price': item['price'],
                    'category': category,
                    'stock': 50,
                    'is_available': True
                }
            )
            
            if p_created:
                # Add Product Variants (Size/Color)
                if 'clothing' in cat_name.lower():
                    sizes = ['Small', 'Medium', 'Large']
                    for size in sizes:
                        ProductVariant.objects.create(product=product, name='Size', value=size, price_modifier=0, stock=random.randint(5, 20))
                else:
                    colors = ['Black', 'Silver']
                    for color in colors:
                        ProductVariant.objects.create(product=product, name='Color', value=color, price_modifier=0, stock=random.randint(5, 20))

                # Download and attach image
                img_url = item.get('image')
                if img_url:
                    try:
                        img_response = requests.get(img_url)
                        if img_response.status_code == 200:
                            file_name = os.path.basename(urllib.parse.urlparse(img_url).path)
                            image_obj = Image.objects.create()
                            image_obj.image_name.save(file_name, ContentFile(img_response.content), save=True)
                            product.product_image.add(image_obj)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Could not download image for {product.name}: {e}"))
                
                self.stdout.write(self.style.SUCCESS(f'Created product and variants: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated database with users, profiles, variants, and real images!'))


