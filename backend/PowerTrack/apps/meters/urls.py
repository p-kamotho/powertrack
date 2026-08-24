from django.urls import path
from .views import *
urlpatterns=[path('',meter_list,name='meter_list'),path('new/',meter_create,name='meter_create')]
