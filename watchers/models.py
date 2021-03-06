from django.db import models

from django_q.models import Schedule

from stocks.models import User, Stock
from stocks.stockdata.wrapper import API_VALID_INTERVALS, API_INTERVALS_VERBOSE
from watchers.task_manager.scheduler import create_schedule


class Watcher(models.Model):

    INTERVALS = {i for i in zip(API_VALID_INTERVALS, API_INTERVALS_VERBOSE)}

    stock = models.ForeignKey(to=Stock, on_delete=models.CASCADE, verbose_name="Ativo")
    upper_threshold = models.FloatField(verbose_name="Limite superior")
    lower_threshold = models.FloatField(verbose_name="Limite inferior")
    # Default interval is 1 day
    interval = models.CharField(
        max_length=5, default=API_VALID_INTERVALS[8], choices=INTERVALS, verbose_name="Intervalo"
    )
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    schedule_id = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Watcher"
        verbose_name_plural = "Watchers"

    def __str__(self):
        return f'{self.stock.code}:[{self.lower_threshold}-{self.upper_threshold}]:{self.interval}'

    def save(self, *args, **kwargs):
        # Save the watcher first to generate an ID
        super().save(*args, **kwargs)
        # print(kwargs['update_fields'])
        self._add_schedule()

    def delete(self, *args, **kwargs):
        self._remove_schedule()
        # Delete the watcher
        super().delete(*args, **kwargs)

    def set_active(self, is_active):
        self.active = is_active

        if is_active:
            self._add_schedule()
        else:
            self._remove_schedule()

    def update_schedule(self):
        self._remove_schedule()
        self._add_schedule()

    def _add_schedule(self):
        if self.active is True and self.schedule_id is None:
            # Create the schedule
            schedule_id = create_schedule(self)

            # Save the model with the schedule id
            self.schedule_id = schedule_id
            super().save(update_fields=['schedule_id'])

    def _remove_schedule(self):
        if self.schedule_id is not None:
            # Delete the schedule
            Schedule.objects.get(pk=self.schedule_id).delete()
            self.schedule_id = None
            super().save(update_fields=['schedule_id'])
