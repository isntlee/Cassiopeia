# Generated by Django 4.1.9 on 2023-06-09 12:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("agents", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agent",
            name="agent_token",
            field=models.CharField(max_length=1000),
        ),
    ]
