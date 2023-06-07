from django.contrib import admin
from .models import Waypoint, Trait


class WaypointAdmin(admin.ModelAdmin):
    list_display = ['waypoint_name']


class TraitAdmin(admin.ModelAdmin):
    list_display = ['symbol']


admin.site.register(Waypoint, WaypointAdmin)
admin.site.register(Trait, TraitAdmin)