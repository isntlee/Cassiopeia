# Generated by Django 4.1.9 on 2023-06-07 15:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("navigation", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="waypoint",
            name="waypoint_name",
            field=models.CharField(default="pre-set", max_length=60),
            preserve_default=False,
        ),
    ]
