from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
# Create your models here.
class Profile (models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length = 100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete = models.CASCADE,related_name='vendor')
    store_name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null= True)
    logo = models.ImageField(upload_to = 'vendor_logos/',blank=True,null=True)
    subscription_plan = models.CharField(max_length=50, choices=[('basic','Basic'),('premium','Premium'),('enterprise','Enterprise')],default='basic') 
    subscription_expiry = models.DateTimeField(blank=True,null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)


    def __str__(self):
        return  self.store_name
    

class Category(models.Model):
   name = models.CharField(max_length = 100)
   slug = models.SlugField(unique=True) 
   parent = models.ForeignKey('self',on_delete=models.CASCADE,blank = True,null =True,related_name = 'children')

   class Meta:
       verbose_name_plural = 'Categories'


   def __str__(self):
       return self.name
       

class Image(models.Model):
    
    image_name = models.ImageField(upload_to = 'product_images/',blank=True,null=True)
    def __str__(self):
        return self.image_name.url if self.image_name else "No image found"

    
class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,
        related_name='products_vendor')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
        related_name='products_category')
    product_image = models.ManyToManyField(Image, 
        related_name='product_image')
    stock = models.PositiveBigIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now= True)


    def __str__(self):
        return self.name
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
        related_name='variants')
    name = models.CharField(max_length=100) #size, #color
    value = models.CharField(max_length=100) #small, medium, large #red, black, blue
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name}:{self.value} for {self.product.name}"


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  #later we will update this using session to make it dynamic
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    shipping_address = models.TextField()
    shipping_method = models.CharField(max_length=100)    
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tracking_number = models.CharField(max_length=100,blank=True,null=True)


    def __str__(self):
        return f'Order #{self.id} by {self.customer.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, blank=True,
        null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} * {self.product.name} in Order #{self.order.id}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=[
        ('khalti', 'Khalti'),
        ('imepay', 'IME Pay'),
        ('esewa', 'Esewa'),
        ('cashondelivery', 'Cash on Delivery')
    ], default='khalti')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"payment for order #{self.order.id}"
    


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
        related_name='reviews_product')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews_customer')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1),
        MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.username} for {self.product.name}"

    

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=50, choices=[
        ("percentage", 'Percentage'),
        ('fixed', "Fixed Amount")
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amout = models.DecimalField(max_digits=10, decimal_places=2,
        blank=True, null=True)
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE,blank=True,null=True,related_name='discounts')



    def __str__(self):
        return self.code
    
class Wishlist(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username}'s Wishlist Item: {self.product.name}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.username}'

#tax variation

class Tax(models.Model):
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=50, blank=True, null=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    applies_to = models.CharField(max_length=50, choices=[
        ('all', 'All Products'),
        ('specific', 'Specific Categories'),
    ], default='all')
    categories = models.ManyToManyField(Category, blank=True)
    
    def __str__(self):
        return f'Tax in {self.country}({self.rate}%)'

class Analytics(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,
        related_name='analytics')
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(default= timezone.now)

    def __str__(self):
        return f"Analytics for {self.vendor.store_name} on {self.date}"

# --- Cart System ---

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} - User: {self.user.username if self.user else 'Guest'}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

    @property
    def total_price(self):
        return self.quantity * self.product.price