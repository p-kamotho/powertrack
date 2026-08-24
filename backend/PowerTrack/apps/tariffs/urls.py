from django.urls import path
from .views import *
urlpatterns=[path('',tariff_list,name='tariff_list'),path('new/',tariff_create,name='tariff_create')]
