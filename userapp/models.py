from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomerUser(AbstractUser):
    is_vendor = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15,blank=True,null=True )