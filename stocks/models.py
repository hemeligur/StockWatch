from django.db import models
from django.contrib.auth.models import AbstractUser


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
