from django import forms
from app1.models import Product

class ProductForm(forms.ModelForm):
    #images = forms.FileField()
    
    class Meta:
        model = Product
        fields = ['name','description','price','category','stock','is_available']
        
    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
        return product

from app1.models import Category
from django.utils.text import slugify

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        
    def save(self, commit=True):
        category = super().save(commit=False)
        if not category.slug:
            category.slug = slugify(category.name)
            
            # Ensure slug is unique
            original_slug = category.slug
            counter = 1
            while Category.objects.filter(slug=category.slug).exists():
                category.slug = f"{original_slug}-{counter}"
                counter += 1
                
        if commit:
            category.save()
        return category