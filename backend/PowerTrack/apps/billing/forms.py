from django import forms
from .models import Bill
class BillForm(forms.ModelForm):
 class Meta:model=Bill;fields=['bill_number','tenant','reading','billing_period','tariff','additional_charges','discount','due_date']
