# Generated by Django 4.2.6 on 2023-11-06 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_fleet_fleet_pricing_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fleet',
            name='efficiency',
        ),
    ]
