from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
import arrow


class User(AbstractUser):
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Envia um email para esse usuário e retorna 1 se sucesso ou 0 se falha."""
        return send_mail(subject, message, from_email, [self.email], **kwargs)


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


class Price(models.Model):
    # Um modelo para implementar uma "cache" para os preços
    # Eventualmente seria bom usar algo como Redis para isso

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateTimeField()

    # Talvez mudar para um IntegerField e armazenar vários
    # tipos de intervalos diferentes (minuto, diário, semanal, mensal)?
    granularity_daily = models.BooleanField(default=True)

    # Os preços daquele momento: Mínima, Abertura, Fechamento e Máxima
    values = models.JSONField()

    class Meta:
        verbose_name = "Price"
        verbose_name_plural = "Prices"
        get_latest_by = "date"

    def __str__(self):
        return f"{self.stock}:{self.date}{'D' if self.granularity_daily else 'M'}"

    @staticmethod
    def bulk_create(price_history, stock_code, granularity_daily=True):
        prices_list = []
        for row in price_history:
            prices_list.append(Price(
                stock=stock_code,
                date=arrow.get(row[0]).datetime,
                granularity_daily=granularity_daily,
                values=row[1:]
            ))
        Price.objects.bulk_create(prices_list)
