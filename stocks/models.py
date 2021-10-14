from django.db import models
from django.contrib.auth.models import AbstractUser

from .stockdata.wrapper import API_VALID_INTERVALS


class User(AbstractUser):
    pass


class Stock(models.Model):

    code = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=50)
    current_price = models.FloatField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return self.name


class StockWatch(models.Model):

    INTERVALS = {(i, i) for i in API_VALID_INTERVALS}

    stock = models.ForeignKey(to="Stock", on_delete=models.CASCADE)
    upper_threshold = models.FloatField()
    lower_threshold = models.FloatField()
    # Default interval is 1 day
    interval = models.CharField(max_length=5, default=API_VALID_INTERVALS[8], choices=INTERVALS)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "StockWatch"
        verbose_name_plural = "StockWatchs"

    def __str__(self):
        return f'{self.stock.code}:[{self.lower_threshold}-{self.upper_threshold}]:{self.interval}'
