from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Stock(models.Model):
    # TODO: Define fields here
    code = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return self.name

class StockWatch(models.Model):

    stock = models.ForeignKey(to="Stock", on_delete=models.CASCADE)
    upper_threshold = models.FloatField()
    lower_threshold = models.FloatField()
    interval = models.PositiveIntegerField(default=(60 * 24))
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "StockWatch"
        verbose_name_plural = "StockWatchs"

    def __str__(self):
        pass
