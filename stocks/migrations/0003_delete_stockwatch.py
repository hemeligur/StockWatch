# Generated by Django 3.2.8 on 2021-10-17 02:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_auto_20211012_0605'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StockWatch',
        ),
    ]