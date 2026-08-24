from django.db import models
from apps.properties.models import Room
class Tenant(models.Model):
    first_name=models.CharField(max_length=100);last_name=models.CharField(max_length=100);phone_number=models.CharField(max_length=20);email=models.EmailField(blank=True);national_id=models.CharField(max_length=50,blank=True)
    room=models.OneToOneField(Room,on_delete=models.SET_NULL,null=True,blank=True,related_name="tenant");move_in_date=models.DateField(null=True,blank=True);move_out_date=models.DateField(null=True,blank=True);is_active=models.BooleanField(default=True)
    @property
    def full_name(self):return f"{self.first_name} {self.last_name}"
    def __str__(self):return self.full_name
