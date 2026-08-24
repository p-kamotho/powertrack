from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Tenant
from .forms import TenantForm
@login_required
def tenant_list(request):return render(request,"tenants/tenant_list.html",{"tenants":Tenant.objects.select_related("room")})
@login_required
def tenant_create(request):
 f=TenantForm(request.POST or None)
 if f.is_valid():f.save();return redirect("tenant_list")
 return render(request,"form.html",{"form":f,"title":"Add Tenant","back":"tenant_list"})
