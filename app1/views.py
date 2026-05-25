from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Vendor
from .serializers import ProductSerializer, CategorySerializer, VendorSerializer

# Keep existing Function Based View for frontend template testing
def homepage(request):
    product = Product.objects.all()
    context = {
        'product': product,
    }
    return render(request, 'app1/index.html', context=context)

@login_required(login_url='/accounts/login/')
def cart_page(request):
    return render(request, 'app1/cart.html')

# --- Class Based Views (DRF ViewSets) ---

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows categories to be viewed.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows products to be viewed.
    Optimized with select_related and prefetch_related.
    """
    # Optimized queryset to prevent N+1 queries problem
    queryset = Product.objects.select_related('vendor', 'category').prefetch_related('product_image', 'variants').filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows vendors to be viewed.
    """
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.AllowAny]

from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer

class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_or_create_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        from django.db.models import prefetch_related_objects
        prefetch_related_objects([cart], 'items__product')
        return cart

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart = self._get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self._get_or_create_cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        return Response({'success': 'Item added to cart'}, status=200)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self._get_or_create_cart(request)
        cart_item_id = request.data.get('cart_item_id')
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
            cart_item.delete()
            return Response({'success': 'Item removed from cart'}, status=200)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=404)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart = self._get_or_create_cart(request)
        
        if not cart.items.exists():
            return Response({'error': 'Your cart is empty.'}, status=400)
            
        shipping_address = request.data.get('shipping_address')
        payment_method = request.data.get('payment_method', 'cashondelivery')
        
        if not shipping_address:
            return Response({'error': 'Shipping address is required.'}, status=400)
            
        from .models import Order, OrderItem, Payment
        
        # 1. Create the Order
        order = Order.objects.create(
            customer=request.user,
            total_amount=cart.total_price,
            shipping_address=shipping_address,
            shipping_method='Standard',
            status='pending'
        )
        
        # 2. Convert CartItems to OrderItems
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
        # 3. Create the Payment Record
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=cart.total_price,
            transaction_id='TXN_PENDING_' + str(order.id)
        )
        
        # 4. Clear the Cart
        cart.items.all().delete()
        
        return Response({'success': 'Order placed successfully!', 'order_id': order.id}, status=201)

from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).select_related('payment').prefetch_related('items__product').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def verify_khalti(self, request, pk=None):
        order = self.get_object()
        token = request.data.get('token')
        amount = request.data.get('amount')
        
        if not token or not amount:
            return Response({'error': 'Token and amount are required.'}, status=400)
            
        # In a real production environment, you would verify this token with Khalti's servers:
        # headers = {'Authorization': 'Key YOUR_KHALTI_SECRET_KEY'}
        # data = {'token': token, 'amount': amount}
        # response = requests.post('https://khalti.com/api/v2/payment/verify/', headers=headers, data=data)
        
        # For this implementation, we will simulate a successful verification
        try:
            payment = order.payment
            payment.status = 'completed'
            payment.transaction_id = token
            payment.payment_method = 'khalti'
            payment.save()
            
            order.status = 'processing'
            order.save()
            
            return Response({'success': 'Payment verified successfully!'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

@login_required(login_url='/accounts/login/')
def orders_page(request):
    return render(request, 'app1/orders.html')
