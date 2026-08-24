from django.db import models
from apps.tenants.models import Tenant
from apps.billing.models import Bill
class Notification(models.Model):
    tenant=models.ForeignKey(Tenant,on_delete=models.CASCADE,related_name="notifications");bill=models.ForeignKey(Bill,on_delete=models.CASCADE,null=True,blank=True);channel=models.CharField(max_length=20,default="EMAIL");subject=models.CharField(max_length=200,blank=True);message=models.TextField();status=models.CharField(max_length=20,default="QUEUED");created_at=models.DateTimeField(auto_now_add=True);sent_at=models.DateTimeField(null=True,blank=True)
    def __str__(self):return f"{self.channel} • {self.tenant.full_name}"
