# Generated by Django 4.2.6 on 2024-01-13 19:27

import accounts.enums
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_remove_business_description_remove_business_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='accept_terms',
            new_name='accept_terms_and_privacy',
        ),
        migrations.AddField(
            model_name='business',
            name='city',
            field=models.CharField(choices=[('ILRN', 'ILORIN')], default=accounts.enums.OperatingCities['ILORIN'], verbose_name='Business city'),
        ),
        migrations.AddField(
            model_name='business',
            name='state',
            field=models.CharField(choices=[('KWARA', 'KWARA')], default=accounts.enums.OperatingStates['KWARA']),
        ),
    ]
