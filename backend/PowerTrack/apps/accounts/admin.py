from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class PowerTrackUserAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets+(("PowerTrack",{"fields":("role","phone_number")}),)
    add_fieldsets=UserAdmin.add_fieldsets+(("PowerTrack",{"fields":("role","phone_number")}),)
    list_display=("username","email","role","is_active")
