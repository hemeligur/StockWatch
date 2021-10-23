# Generated by Django 3.2.8 on 2021-10-23 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchers', '0006_alter_watcher_interval'),
    ]

    operations = [
        migrations.RenameField(
            model_name='watcher',
            old_name='schedule_id',
            new_name='schedule',
        ),
        migrations.AlterField(
            model_name='watcher',
            name='interval',
            field=models.CharField(choices=[('1m', '1m'), ('1h', '1h'), ('2m', '2m'), ('15m', '15m'), ('5m', '5m'), ('90m', '90m'), ('60m', '60m'), ('5d', '5d'), ('1wk', '1wk'), ('1mo', '1mo'), ('30m', '30m'), ('3mo', '3mo'), ('1d', '1d')], default='1d', max_length=5, verbose_name='Intervalo'),
        ),
    ]
