from django.db import models


class Ship(models.Model):
    ship_name = models.CharField(max_length=60)
    faction = models.CharField(max_length=60)
    role = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    departure_symbol = models.CharField(max_length=60)
    departure_type = models.CharField(max_length=60)
    departure_longitude = models.IntegerField(null=True, blank=True)
    departure_latitude = models.IntegerField(null=True, blank=True)

    destination_symbol = models.CharField(max_length=60)
    destination_type = models.CharField(max_length=60)
    destination_longitude = models.IntegerField(null=True, blank=True)
    destination_latitude = models.IntegerField(null=True, blank=True)

    fuel_current = models.IntegerField(null=True, blank=True)
    fuel_capacity = models.IntegerField(null=True, blank=True)
    fuel_consumed = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ship_name:
            return
        super(Ship, self).save(*args, **kwargs)

    def __str__(self):
        return self.ship_name


#  Keep cargo seperate until running cargo request
## ADD CARGO HERE 