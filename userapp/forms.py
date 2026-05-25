from django import forms
from django.contrib.auth.forms import UserCreationForm
from . models import CustomerUser
from app1.models import Vendor

class UserSignupForm(UserCreationForm):
    is_vendor = forms.BooleanField(required=False, help_text="Check if you want to register as a vendor.")

    class Meta:
        model = CustomerUser
        fields = ['username', 'email', 'password1', 'password2', 'is_vendor']

class VendorSignupForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['store_name', 'description', 'logo']
