from django.urls import path
from .views import *
urlpatterns=[path('',reading_list,name='reading_list'),path('new/',reading_create,name='reading_create'),path('periods/',period_list,name='period_list'),path('periods/new/',period_create,name='period_create')]
