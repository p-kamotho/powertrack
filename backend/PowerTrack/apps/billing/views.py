from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Bill
from .forms import BillForm
@login_required
def bill_list(request):return render(request,"billing/bill_list.html",{"bills":Bill.objects.select_related("tenant","billing_period","tariff")})
@login_required
def bill_create(request):
 f=BillForm(request.POST or None)
 if f.is_valid():f.save();return redirect("bill_list")
 return render(request,"form.html",{"form":f,"title":"Generate Bill","back":"bill_list"})
