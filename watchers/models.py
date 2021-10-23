from django.db import models

from django_q.models import Schedule

from stocks.models import User, Stock
from stocks.stockdata.wrapper import API_VALID_INTERVALS
from watchers.task_manager.scheduler import create_schedule


class Watcher(models.Model):

    INTERVALS = {(i, i) for i in API_VALID_INTERVALS}

    stock = models.ForeignKey(to=Stock, on_delete=models.CASCADE, verbose_name="Ativo")
    upper_threshold = models.FloatField(verbose_name="Limite superior")
    lower_threshold = models.FloatField(verbose_name="Limite inferior")
    # Default interval is 1 day
    interval = models.CharField(
        max_length=5, default=API_VALID_INTERVALS[8], choices=INTERVALS, verbose_name="Intervalo"
    )
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    schedule = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Watcher"
        verbose_name_plural = "Watcher"

    def __str__(self):
        return f'{self.stock.code}:[{self.lower_threshold}-{self.upper_threshold}]:{self.interval}'

    def save(self, *args, **kwargs):
        # Save the watcher first to generate an ID
        super().save(*args, **kwargs)

        self.add_schedule()

    def delete(self, *args, **kwargs):
        self.remove_schedule()
        # Delete the watcher
        super().delete(*args, **kwargs)

    def add_schedule(self):
        if self.schedule is None:
            # Create the schedule
            schedule = create_schedule(self)

            # Save the model with the schedule id
            self.schedule = schedule
            super().save(update_fields=['schedule'])

    def remove_schedule(self):
        if self.schedule is not None:
            # Delete the schedule
            Schedule.objects.get(pk=self.schedule).delete()
            self.schedule = None
            super().save(update_fields=['schedule'])
