from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .services import dashboard_metrics

@login_required
def dashboard(request):
    summary = dashboard_metrics()
    metrics = [
        ("Meters", summary["meter_count"], "bi-speedometer2"),
        ("Readings", summary["reading_count"], "bi-activity"),
        ("Bills", summary["bill_count"], "bi-receipt"),
        ("Payments", summary["payment_count"], "bi-wallet2"),
    ]
    return render(request, "dashboard/dashboard.html", {"summary": summary, "metrics": metrics})

@login_required
def dashboard_data(request):
    return JsonResponse(dashboard_metrics())
