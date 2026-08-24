from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect,render
def login_view(request):
    if request.user.is_authenticated:return redirect("dashboard")
    form=AuthenticationForm(request,data=request.POST or None)
    if form.is_valid(): login(request,form.get_user()); return redirect("dashboard")
    return render(request,"accounts/login.html",{"form":form})
