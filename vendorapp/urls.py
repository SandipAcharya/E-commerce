from django.contrib import admin
from django.urls import path
from  vendorapp import views

urlpatterns = [
    
    path("vdash/",views.vendordashboard,name = "vdash"),
    path("vdash/add-product/",views.add_product,name = "add-product"),
    path("vdash/add-category/", views.add_category, name="add-category"),
    path("vdash/update-product/<int:pk>/",views.update_product,name = "update-product"),
    path("vdash/delete-product/<int:pk>/",views.delete_product,name = "delete-product"),
    path("become-vendor/", views.become_vendor, name="become_vendor"),
]
