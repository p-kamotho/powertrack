from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import BillingPeriod,MeterReading
from .forms import BillingPeriodForm,MeterReadingForm
@login_required
def reading_list(request):return render(request,"readings/reading_list.html",{"readings":MeterReading.objects.select_related("meter","billing_period")})
@login_required
def reading_create(request):
 f=MeterReadingForm(request.POST or None)
 if f.is_valid():f.save();return redirect("reading_list")
 return render(request,"form.html",{"form":f,"title":"Enter Meter Reading","back":"reading_list"})
@login_required
def period_list(request):return render(request,"readings/period_list.html",{"periods":BillingPeriod.objects.all()})
@login_required
def period_create(request):
 f=BillingPeriodForm(request.POST or None)
 if f.is_valid():f.save();return redirect("period_list")
 return render(request,"form.html",{"form":f,"title":"Create Billing Period","back":"period_list"})
