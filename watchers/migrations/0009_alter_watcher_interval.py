# Generated by Django 3.2.8 on 2021-10-23 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchers', '0008_alter_watcher_interval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watcher',
            name='interval',
            field=models.CharField(choices=[('5d', '5d'), ('5m', '5m'), ('2m', '2m'), ('1m', '1m'), ('1d', '1d'), ('1wk', '1wk'), ('3mo', '3mo'), ('30m', '30m'), ('90m', '90m'), ('15m', '15m'), ('60m', '60m'), ('1mo', '1mo'), ('1h', '1h')], default='1d', max_length=5, verbose_name='Intervalo'),
        ),
    ]
