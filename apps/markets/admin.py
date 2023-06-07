from django.contrib import admin
from .models import Market, Good, TradeGood

class MarketAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'created_at']

class TradeGoodAdmin(admin.ModelAdmin):
    list_display = ['tradegood_name', 'sellPrice', 'purchasePrice', 'updated_at']

class GoodAdmin(admin.ModelAdmin):
    list_display = ['symbol']

admin.site.register(Market, MarketAdmin)
admin.site.register(TradeGood, TradeGoodAdmin)
admin.site.register(Good, GoodAdmin)