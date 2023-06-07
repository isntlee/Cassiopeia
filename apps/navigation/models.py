from django.db import models


class Waypoint(models.Model):
    waypoint_name = models.CharField(max_length=60)
    systemSymbol = models.CharField(max_length=60)
    symbol = models.CharField(max_length=60)
    type = models.CharField(max_length=60)
    coords_long = models.IntegerField(null=True, blank=True)
    coords_lat = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    faction = models.CharField(max_length=60)
    traits = models.ManyToManyField('Trait', through='WaypointTraits')

    def save(self, *args, **kwargs):
        if not self.symbol:
            return
        self.waypoint_name = f"{self.symbol}-{self.type}"
        super(Waypoint, self).save(*args, **kwargs)

    def __str__(self):
        return self.waypoint_name


class Trait(models.Model):
    symbol = models.CharField(max_length=60)
    description = models.CharField(max_length=300)
    waypoints = models.ManyToManyField('Waypoint', through='WaypointTraits')


class WaypointTraits(models.Model):
    trait = models.ForeignKey(Waypoint, null=True, on_delete=models.SET_NULL)
    waypoint = models.ForeignKey(Trait, null=True, on_delete=models.SET_NULL)
