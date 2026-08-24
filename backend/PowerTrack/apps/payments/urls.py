from django.urls import path
from .views import *
urlpatterns=[path('',payment_list,name='payment_list'),path('new/',payment_create,name='payment_create')]
