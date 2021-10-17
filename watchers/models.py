from django.db import models

from stocks.models import User, Stock
from stocks.stockdata.wrapper import API_VALID_INTERVALS

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

    class Meta:
        verbose_name = "Watcher"
        verbose_name_plural = "Watcher"

    def __str__(self):
        return f'{self.stock.code}:[{self.lower_threshold}-{self.upper_threshold}]:{self.interval}'