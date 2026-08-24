from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Property,Room
from .forms import PropertyForm,RoomForm
@login_required
def property_list(request):return render(request,"properties/property_list.html",{"properties":Property.objects.all()})
@login_required
def property_create(request):
    f=PropertyForm(request.POST or None)
    if f.is_valid():f.save();return redirect("property_list")
    return render(request,"form.html",{"form":f,"title":"Add Property","back":"property_list"})
@login_required
def room_list(request):return render(request,"properties/room_list.html",{"rooms":Room.objects.select_related("property","tenant","meter")})
@login_required
def room_create(request):
    f=RoomForm(request.POST or None)
    if f.is_valid():f.save();return redirect("room_list")
    return render(request,"form.html",{"form":f,"title":"Add Room","back":"room_list"})
