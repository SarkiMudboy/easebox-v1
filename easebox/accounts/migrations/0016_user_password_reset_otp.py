# Generated by Django 4.2.6 on 2024-02-21 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_user_active_password_reset_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password_reset_otp',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True),
        ),
    ]
