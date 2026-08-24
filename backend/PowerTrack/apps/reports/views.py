from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .services import billing_summary, consumption_csv, consumption_rows

@login_required
def report_home(request):
    return render(request, "reports/report_home.html", {"summary": billing_summary()})

@login_required
def consumption_report(request):
    return render(request, "reports/consumption_report.html", {"rows": consumption_rows()})

@login_required
def consumption_csv_download(request):
    response = HttpResponse(consumption_csv(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="powertrack_consumption.csv"'
    return response
