from django.urls import path
from .views import report_home, consumption_report, consumption_csv_download

urlpatterns = [
    path("", report_home, name="report_home"),
    path("consumption/", consumption_report, name="consumption_report"),
    path("consumption.csv", consumption_csv_download, name="consumption_csv"),
]
