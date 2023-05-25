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
    tradeVolume = models.IntegerField(null=True, blank=True)
    supply = models.CharField(max_length=30, null=True, blank=True)
    market = models.ForeignKey(Market, related_name='goods', on_delete=models.CASCADE)
    purchasePrice = models.IntegerField(null=True, blank=True)
    sellPrice = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.symbol
