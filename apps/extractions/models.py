from django.db import models

class Extraction(models.Model):
    ship = models.CharField(max_length=60)
    extracted = models.CharField(max_length=60)
    units = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    cooldown = models.IntegerField(null=True, blank=True)

    cargo_capacity = models.IntegerField(null=True, blank=True)
    units_held = models.IntegerField(null=True, blank=True)
    cargo_fill = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    full_cargo = models.BooleanField(default=False)
    extraction_name = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.ship:
            return
        self.extraction_name = f"{self.id}-{self.ship}-{self.extracted}"
        super(Extraction, self).save(*args, **kwargs)

    def __str__(self):
        return self.extraction_name


#  Keep cargo seperate until running cargo request




