# Generated by Django 3.2.8 on 2021-10-21 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchers', '0003_alter_watcher_interval'),
    ]

    operations = [
        migrations.AddField(
            model_name='watcher',
            name='schedule_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='watcher',
            name='interval',
            field=models.CharField(choices=[('5m', '5m'), ('2m', '2m'), ('1m', '1m'), ('60m', '60m'), ('5d', '5d'), ('1wk', '1wk'), ('1mo', '1mo'), ('1d', '1d'), ('3mo', '3mo'), ('15m', '15m'), ('1h', '1h'), ('90m', '90m'), ('30m', '30m')], default='1d', max_length=5, verbose_name='Intervalo'),
        ),
    ]
