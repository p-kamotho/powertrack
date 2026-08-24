from django.urls import path
from .views import *
urlpatterns=[path('',bill_list,name='bill_list'),path('new/',bill_create,name='bill_create')]
