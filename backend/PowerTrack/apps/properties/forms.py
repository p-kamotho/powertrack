from django import forms
from .models import Property,Room
class PropertyForm(forms.ModelForm):
    class Meta:model=Property;fields=["name","address","description","is_active"]
class RoomForm(forms.ModelForm):
    class Meta:model=Room;fields=["property","room_number","status","floor","description"]
