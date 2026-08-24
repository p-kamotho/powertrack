from django.db import models
from apps.billing.models import Bill
class Payment(models.Model):
    class Method(models.TextChoices): CASH="CASH","Cash";MPESA="MPESA","M-Pesa";BANK="BANK","Bank";OTHER="OTHER","Other"
    bill=models.ForeignKey(Bill,on_delete=models.PROTECT,related_name="payments");amount=models.DecimalField(max_digits=12,decimal_places=2);method=models.CharField(max_length=20,choices=Method.choices);reference=models.CharField(max_length=100,blank=True);paid_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):return self.reference or str(self.pk)
