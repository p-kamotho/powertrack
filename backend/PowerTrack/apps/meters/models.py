from django.db import models
from apps.properties.models import Room
class Meter(models.Model):
    class Status(models.TextChoices): ACTIVE="ACTIVE","Active";INACTIVE="INACTIVE","Inactive";FAULTY="FAULTY","Faulty"
    meter_number=models.CharField(max_length=100,unique=True);room=models.OneToOneField(Room,on_delete=models.PROTECT,related_name="meter");status=models.CharField(max_length=20,choices=Status.choices,default=Status.ACTIVE);installation_date=models.DateField(null=True,blank=True);initial_reading=models.DecimalField(max_digits=12,decimal_places=2,default=0);notes=models.TextField(blank=True)
    def __str__(self):return self.meter_number
