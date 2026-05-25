from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages
from .forms import UserSignupForm, VendorSignupForm
from app1.models import Profile 
from .models import CustomerUser
 # we will use  later oauth library (enterprise practice)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        # Safer extraction method to avoid MultiValueDictKeyError crashes
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successful')
            return redirect('index')
        else:
            messages.error(request, 'Invalid Username or Password')
            
    return render(request, 'userapp/login.html')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logout successfully.')
    else:
        messages.warning(request, 'You are not logged in.')
    return redirect('index')

def signup(request):
    if request.method == "POST":
        user_form = UserSignupForm(request.POST)
        vendor_form = VendorSignupForm(request.POST, request.FILES)
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.is_vendor = user_form.cleaned_data['is_vendor']
            user.save()
            Profile.objects.create(user=user)
            if user.is_vendor and vendor_form.is_valid():
                vendor = vendor_form.save(commit=False)
                vendor.user = user
                vendor.save()
            login(request, user)
            return redirect('index')
    else:
        user_form = UserSignupForm()
        vendor_form = VendorSignupForm()
    return render(request, 'userapp/signup.html', {'user_form': user_form,
                                                    'vendor_form': vendor_form})

   
