from django import forms
from .models import Tariff
class TariffForm(forms.ModelForm):
 class Meta:model=Tariff;fields='__all__'
