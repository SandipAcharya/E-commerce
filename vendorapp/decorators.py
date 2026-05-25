from functools import wraps
from django.shortcuts import redirect

def vendor_required(view_func):
    @wraps(view_func)
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated and request.user.is_vendor:
            return view_func(request,*args,**kwargs)
        return redirect('vdash')
    return wrapper