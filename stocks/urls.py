from django.urls import path
from .views import StockSearchView, StockDetailView

app_name = "stocks"

urlpatterns = [
    path('search/', StockSearchView.as_view(), name="stock_search"),
    path('<pk>/', StockDetailView.as_view(), name="stock_detail")
]
