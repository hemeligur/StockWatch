from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Stock(models.Model):
    # TODO: Define fields here
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

    INTERVALS = {
        ("1m", "1m"),
        ("2m", "2m"),
        ("5m", "5m"),
        ("15m", "15m"),
        ("30m", "30m"),
        ("60m", "60m"),
        ("90m", "90m"),
        ("1h", "1h"),
        ("1d", "1d"),
        ("5d", "5d"),
        ("1wk", "1wk"),
        ("1mo", "1mo"),
        ("3mo", "3mo")

    }

    stock = models.ForeignKey(to="Stock", on_delete=models.CASCADE)
    upper_threshold = models.FloatField()
    lower_threshold = models.FloatField()
    interval = models.CharField(max_length=5, default="1d", choices=INTERVALS)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "StockWatch"
        verbose_name_plural = "StockWatchs"

    def __str__(self):
        pass
