# Generated by Django 3.2.8 on 2021-10-23 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchers', '0005_auto_20211023_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watcher',
            name='interval',
            field=models.CharField(choices=[('1mo', '1mo'), ('5m', '5m'), ('2m', '2m'), ('30m', '30m'), ('1h', '1h'), ('5d', '5d'), ('90m', '90m'), ('60m', '60m'), ('1wk', '1wk'), ('3mo', '3mo'), ('15m', '15m'), ('1d', '1d'), ('1m', '1m')], default='1d', max_length=5, verbose_name='Intervalo'),
        ),
    ]
