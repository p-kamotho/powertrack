from django.urls import path
from .views import *
urlpatterns=[path('',tenant_list,name='tenant_list'),path('new/',tenant_create,name='tenant_create')]
