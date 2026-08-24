from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Meter
from .forms import MeterForm
@login_required
def meter_list(request):return render(request,"meters/meter_list.html",{"meters":Meter.objects.select_related("room","room__property")})
@login_required
def meter_create(request):
 f=MeterForm(request.POST or None)
 if f.is_valid():f.save();return redirect("meter_list")
 return render(request,"form.html",{"form":f,"title":"Register Meter","back":"meter_list"})
