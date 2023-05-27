# Generated by Django 4.1.9 on 2023-05-27 16:17

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ship",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ship_name", models.CharField(max_length=60)),
                ("faction", models.CharField(max_length=60)),
                ("role", models.CharField(max_length=60)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("departure", models.CharField(max_length=60)),
                ("departure_symbol", models.CharField(max_length=60)),
                ("departure_type", models.CharField(max_length=60)),
                ("departure_longitude", models.IntegerField(blank=True, null=True)),
                ("departure_latitude", models.IntegerField(blank=True, null=True)),
                ("destination", models.CharField(max_length=60)),
                ("destination_symbol", models.CharField(max_length=60)),
                ("destination_type", models.CharField(max_length=60)),
                ("destination_longitude", models.IntegerField(blank=True, null=True)),
                ("destination_latitude", models.IntegerField(blank=True, null=True)),
                ("fuel_current", models.IntegerField(blank=True, null=True)),
                ("fuel_capacity", models.IntegerField(blank=True, null=True)),
                ("fuel_consumed", models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
