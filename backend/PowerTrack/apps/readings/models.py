from django.db import models
from django.core.exceptions import ValidationError
from apps.meters.models import Meter
class BillingPeriod(models.Model):
    name=models.CharField(max_length=100);start_date=models.DateField();end_date=models.DateField();is_closed=models.BooleanField(default=False)
    def clean(self):
        if self.end_date<self.start_date:raise ValidationError("End date cannot be before start date.")
    def __str__(self):return self.name
class MeterReading(models.Model):
    meter=models.ForeignKey(Meter,on_delete=models.PROTECT,related_name="readings");billing_period=models.ForeignKey(BillingPeriod,on_delete=models.PROTECT,related_name="readings");reading_date=models.DateField();previous_reading=models.DecimalField(max_digits=12,decimal_places=2);current_reading=models.DecimalField(max_digits=12,decimal_places=2);consumption=models.DecimalField(max_digits=12,decimal_places=2,default=0,editable=False);notes=models.TextField(blank=True)
    class Meta:constraints=[models.UniqueConstraint(fields=["meter","billing_period"],name="unique_meter_reading_per_period")]
    def clean(self):
        if self.current_reading<self.previous_reading:raise ValidationError("Current reading cannot be lower than previous reading.")
        if self.billing_period.is_closed:raise ValidationError("Billing period is closed.")
    def save(self,*a,**kw):
        self.consumption=self.current_reading-self.previous_reading;self.full_clean();return super().save(*a,**kw)
