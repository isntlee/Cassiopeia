from django.db import models


class Market(models.Model):
    symbol = models.CharField(max_length=60)
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
    tradegood_name = models.CharField(max_length=60)
    tradeVolume = models.IntegerField(null=True, blank=True)
    supply = models.CharField(max_length=30, null=True, blank=True)
    purchasePrice = models.IntegerField(null=True, blank=True)
    sellPrice = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    good = models.ForeignKey(Good, related_name='tradegoods', on_delete=models.CASCADE)
    market = models.ForeignKey(Market, related_name='tradegoods', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.tradegood_name
