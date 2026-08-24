from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Payment
from .forms import PaymentForm
@login_required
def payment_list(request):return render(request,"payments/payment_list.html",{"payments":Payment.objects.select_related("bill","bill__tenant")})
@login_required
def payment_create(request):
 f=PaymentForm(request.POST or None)
 if f.is_valid():
  p=f.save();p.bill.amount_paid=sum(x.amount for x in p.bill.payments.all());p.bill.save();return redirect("payment_list")
 return render(request,"form.html",{"form":f,"title":"Record Payment","back":"payment_list"})
