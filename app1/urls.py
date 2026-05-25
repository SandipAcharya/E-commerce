from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'vendors', views.VendorViewSet, basename='vendor')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='orders')

urlpatterns = [
    # FBV for testing standard template rendering
    path('', views.homepage, name='index'),
    path('cart/', views.cart_page, name='cart_page'),
    path('orders/', views.orders_page, name='orders_page'),
    
    # CBV API endpoints
    path('api/', include(router.urls)),
]
