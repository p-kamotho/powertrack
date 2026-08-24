from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN="ADMIN","Administrator"; MANAGER="MANAGER","Property Manager"; METER_READER="METER_READER","Meter Reader"; TENANT="TENANT","Tenant"
    role=models.CharField(max_length=20,choices=Role.choices,default=Role.MANAGER)
    phone_number=models.CharField(max_length=20,blank=True)
    def __str__(self): return self.get_full_name() or self.username
