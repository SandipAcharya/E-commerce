from django.shortcuts import render,redirect
from .decorators import vendor_required
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from app1.models import Product, Image
# Create your views here.
@login_required(login_url='/accounts/login/')
@vendor_required
def vendordashboard(request):
    vendor = getattr(request.user, 'vendor', None)
    if not vendor:
        return redirect('index')
    
    products = Product.objects.filter(vendor=vendor).order_by('-created_at')
    context = {'products': products}
    return render(request,'vendorapp/vendordashboard.html',context = context)

@login_required
@vendor_required
def add_product(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('vdash')
        
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        images = request.FILES.getlist('images')
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()

            for img in images:
                image_obj = Image.objects.create(image_name = img)
                product.product_image.add(image_obj)
                product.save()
            return redirect('vdash')
    else:
        form = ProductForm()
    return render(request,'vendorapp/add_product.html',{'form':form})

@login_required(login_url='/accounts/login/')
def become_vendor(request):
    if request.user.is_vendor:
        return redirect('vdash')
        
    if request.method == 'POST':
        store_name = request.POST.get('store_name')
        description = request.POST.get('description')
        
        if store_name:
            # Upgrade user to vendor
            request.user.is_vendor = True
            request.user.save()
            
            # Create vendor profile
            from app1.models import Vendor
            Vendor.objects.create(
                user=request.user,
                store_name=store_name,
                description=description
            )
            return redirect('vdash')
    return render(request, 'vendorapp/become_vendor.html')

from django.shortcuts import get_object_or_404

@login_required(login_url='/accounts/login/')
@vendor_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user.vendor)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        images = request.FILES.getlist('images')
        if form.is_valid():
            product = form.save()
            
            # Optional: handle new images
            if images:
                for img in images:
                    image_obj = Image.objects.create(image_name=img)
                    product.product_image.add(image_obj)
            return redirect('vdash')
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'vendorapp/add_product.html', {'form': form, 'is_update': True})

@login_required(login_url='/accounts/login/')
@vendor_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user.vendor)
    if request.method == 'POST':
        product.delete()
    return redirect('vdash')

from .forms import CategoryForm

@login_required(login_url='/accounts/login/')
@vendor_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to add-product after creating category so they can use it
            return redirect('add-product') 
    else:
        form = CategoryForm()
        
    return render(request, 'vendorapp/add_category.html', {'form': form})