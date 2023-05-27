from django.contrib import admin
from .models import Ship


class ShipAdmin(admin.ModelAdmin):
    list_display = ['ship_name', 'role', 'destination_type', 'fuel_current' , 'fuel_capacity']

admin.site.register(Ship, ShipAdmin)