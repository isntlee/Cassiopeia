from django.contrib import admin
from .models import Ship, Cargo, CargoLoad


class ShipAdmin(admin.ModelAdmin):
    list_display = ['ship_name', 'role', 'destination_type', 'fuel_current' , 'fuel_capacity']

class CargoAdmin(admin.ModelAdmin):
    list_display = ['cargo_name', 'cargo_fill', 'updated_at']

class CargoLoadAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'units', 'cargo', 'updated_at']


admin.site.register(Ship, ShipAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(CargoLoad, CargoLoadAdmin)