from django.contrib import admin
from .models import Market, Good

class MarketAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'created_at']
    fields = ['symbol']

admin.site.register(Market, MarketAdmin)
admin.site.register(Good)