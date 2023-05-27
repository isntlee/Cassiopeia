from django.contrib import admin
from .models import Market, Good, TradeGood

class MarketAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'created_at']
    fields = ['symbol']

class TradeGoodAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'sellPrice', 'purchasePrice']
    fields = ['symbol', 'supply', 'tradeVolume']

class GoodAdmin(admin.ModelAdmin):
    list_display = ['symbol']
    fields = ['symbol']

admin.site.register(Market, MarketAdmin)
admin.site.register(TradeGood, TradeGoodAdmin)
admin.site.register(Good, GoodAdmin)