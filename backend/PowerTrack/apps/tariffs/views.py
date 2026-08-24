from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Tariff
from .forms import TariffForm
@login_required
def tariff_list(request):return render(request,"tariffs/tariff_list.html",{"tariffs":Tariff.objects.all()})
@login_required
def tariff_create(request):
 f=TariffForm(request.POST or None)
 if f.is_valid():f.save();return redirect("tariff_list")
 return render(request,"form.html",{"form":f,"title":"Add Tariff","back":"tariff_list"})
