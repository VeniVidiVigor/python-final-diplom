# Generated by Django 5.1.4 on 2025-01-03 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_shop_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinfo',
            name='external_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Внешний ID'),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='model',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Модель'),
        ),
    ]
