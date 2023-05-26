from django.db import models


class Market(models.Model):
    symbol = models.CharField(max_length=60)
    type = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.symbol:
            return
        super(Market, self).save(*args, **kwargs)

    def __str__(self):
        return self.symbol


class Good(models.Model):
    symbol = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.symbol


class TradeGood(models.Model):
    symbol = models.CharField(max_length=30)
    tradeVolume = models.IntegerField(null=True, blank=True)
    supply = models.CharField(max_length=30, null=True, blank=True)
    purchasePrice = models.IntegerField(null=True, blank=True)
    sellPrice = models.IntegerField(null=True, blank=True)
    markets = models.ManyToManyField(Market, through='MarketTrade')
    good = models.ForeignKey(Good, related_name='tradegoods', on_delete=models.CASCADE)

    def __str__(self):
        return self.symbol
    

class MarketTrade(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    tradegood = models.ForeignKey(TradeGood, on_delete=models.CASCADE)