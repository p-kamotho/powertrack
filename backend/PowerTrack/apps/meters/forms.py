from django import forms
from .models import Meter
class MeterForm(forms.ModelForm):
 class Meta:model=Meter;fields='__all__'
