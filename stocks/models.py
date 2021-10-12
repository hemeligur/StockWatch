from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import yfinance as yf


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

    # Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    def get_history(self, period="6mo", start_date=None, end_date=None, interval="1d"):
        ticker = yf.Ticker(self.code)

        # Validations
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "90m",
                           "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

        try:
            interval_idx = valid_intervals.index(interval)
            period_idx = valid_periods.index(period)

            if interval_idx <= 5 and period_idx > 2:
                raise ValueError(
                    f"For interval {interval} the requested period must be within the last 60 days")
            elif interval_idx >= 6 and interval_idx <= 7 and period_idx > 6:
                raise ValueError(
                    f"For interval {interval} the requested period must be within the last 2 years")

        except ValueError as err:
            # TODO
            print("invalid interval and/or period:", err)
            raise

        if start_date is not None:
            end_date = end_date if end_date is not None else timezone.now()
            history = ticker.history(start=start_date, end=end_date)
        else:
            history = ticker.history(period=period)

        return history

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
