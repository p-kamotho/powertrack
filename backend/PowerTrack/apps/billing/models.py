from django.db import models
from apps.tenants.models import Tenant
from apps.readings.models import MeterReading,BillingPeriod
from apps.tariffs.models import Tariff
class Bill(models.Model):
    class Status(models.TextChoices): ISSUED="ISSUED","Issued";PARTIAL="PARTIAL","Partially Paid";PAID="PAID","Paid";OVERDUE="OVERDUE","Overdue";CANCELLED="CANCELLED","Cancelled"
    bill_number=models.CharField(max_length=60,unique=True);tenant=models.ForeignKey(Tenant,on_delete=models.PROTECT,related_name="bills");reading=models.OneToOneField(MeterReading,on_delete=models.PROTECT,related_name="bill");billing_period=models.ForeignKey(BillingPeriod,on_delete=models.PROTECT,related_name="bills");tariff=models.ForeignKey(Tariff,on_delete=models.PROTECT,related_name="bills");consumption=models.DecimalField(max_digits=12,decimal_places=2,default=0);energy_charge=models.DecimalField(max_digits=12,decimal_places=2,default=0);additional_charges=models.DecimalField(max_digits=12,decimal_places=2,default=0);discount=models.DecimalField(max_digits=12,decimal_places=2,default=0);total_amount=models.DecimalField(max_digits=12,decimal_places=2,default=0);amount_paid=models.DecimalField(max_digits=12,decimal_places=2,default=0);balance=models.DecimalField(max_digits=12,decimal_places=2,default=0);due_date=models.DateField(null=True,blank=True);status=models.CharField(max_length=20,choices=Status.choices,default=Status.ISSUED);created_at=models.DateTimeField(auto_now_add=True)
    def save(self,*a,**kw):
        self.consumption=self.reading.consumption
        self.energy_charge=self.consumption*self.tariff.rate_per_kwh
        self.total_amount=self.energy_charge+self.additional_charges-self.discount
        self.balance=max(0,self.total_amount-self.amount_paid)
        self.status=self.Status.PAID if self.amount_paid>=self.total_amount and self.total_amount>0 else self.Status.PARTIAL if self.amount_paid>0 else self.Status.ISSUED
        return super().save(*a,**kw)
    def __str__(self):return self.bill_number
