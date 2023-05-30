from django.db import models
from markets.models import Good


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

    flightmode=models.CharField(max_length=60)
    ship_status=models.CharField(max_length=60)
    location_current=models.CharField(max_length=60)
    location_current_type=models.CharField(max_length=60)

    def save(self, *args, **kwargs):
        if not self.ship_name:
            return
        super(Ship, self).save(*args, **kwargs)

    def __str__(self):
        return self.ship_name


class Cargo(models.Model):
    cargo_name = models.CharField(max_length=60)
    cargo_capacity = models.IntegerField(null=True, blank=True)
    units_held = models.IntegerField(null=True, blank=True)
    cargo_fill = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    full_cargo = models.BooleanField(default=False)
    ship = models.OneToOneField(Ship, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.ship:
            return
        self.cargo_name = f"{self.ship}-cargo"
        super(Cargo, self).save(*args, **kwargs)

    def __str__(self):
        return self.cargo_name
    

class CargoLoad(models.Model):
    symbol = models.CharField(max_length=60)
    units = models.IntegerField(null=True, blank=True)
    good = models.ForeignKey(Good, related_name='cargogoods', on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, related_name='cargoload', on_delete=models.CASCADE)

    def __str__(self):
        return self.symbol