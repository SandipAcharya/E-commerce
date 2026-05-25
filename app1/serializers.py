from rest_framework import serializers
from .models import Product, Category, ProductVariant, Image, Vendor, Cart, CartItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_name']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'value', 'price_modifier', 'stock']

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'store_name', 'description', 'logo']

class ProductSerializer(serializers.ModelSerializer):
    # Nested relationships for read representation
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    
    variants = ProductVariantSerializer(many=True, read_only=True)
    product_image = ImageSerializer(many=True, read_only=True)
    
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'vendor', 'name', 'description', 'price', 
            'category', 'category_id', 'product_image', 'variants', 
            'stock', 'is_available', 'created_at', 'updated_at'
        ]

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at']

from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='items')
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_amount', 'shipping_address', 'shipping_method', 'status', 'created_at', 'order_items']
        read_only_fields = ['customer', 'total_amount']
