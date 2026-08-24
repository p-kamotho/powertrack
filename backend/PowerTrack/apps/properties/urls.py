from django.urls import path
from .views import *
urlpatterns=[path('',property_list,name='property_list'),path('new/',property_create,name='property_create'),path('rooms/',room_list,name='room_list'),path('rooms/new/',room_create,name='room_create')]
