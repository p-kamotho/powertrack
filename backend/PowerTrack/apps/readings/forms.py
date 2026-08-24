from django import forms
from .models import BillingPeriod,MeterReading
class BillingPeriodForm(forms.ModelForm):
 class Meta:model=BillingPeriod;fields='__all__'
class MeterReadingForm(forms.ModelForm):
 class Meta:model=MeterReading;fields=['meter','billing_period','reading_date','previous_reading','current_reading','notes']
