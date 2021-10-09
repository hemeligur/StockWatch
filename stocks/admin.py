from django.contrib import admin
from .models import User, Stock, StockWatch

admin.site.register(User)
admin.site.register(Stock)
admin.site.register(StockWatch)
