from django.urls import path
from .views import dashboard, dashboard_data
urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("data/", dashboard_data, name="dashboard_data"),
]
