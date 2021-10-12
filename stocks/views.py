from django.views.generic import TemplateView, DetailView
from django.http import Http404
from django.utils import timezone

import yfinance as yf

from .models import Stock


class LandingPageView(TemplateView):
    template_name = "landing_page.html"


class StockSearchView(TemplateView):
    template_name = "stocks/stock_search.html"

    def get(self, request):
        query = request.GET.get('q')
        if query:
            pass


class StockDetailView(DetailView):
    model = Stock
    template_name = "stocks/stock_detail.html"
    context_object_name = "stock"
    stock_data = None

    def get_object(self):
        # Tenta buscar o ativo no DB.
        # Se não encontrar, é a primeira vez que esse ativo é visualizado.
        # Então é feita uma chamada a API para criar um novo ativo.
        try:
            obj = super().get_object()
        except Http404:
            code = self.kwargs.get(self.pk_url_kwarg)
            symbol = code + ".SA"
            self.stock_data = yf.Ticker(symbol)

            info = self.stock_data.info
            if 'longName' in info and 'symbol' in info:
                obj = Stock(
                    code=code,
                    name=info['longName'],
                    current_price=info['currentPrice'],
                    last_update=timezone.now()
                )
                obj.save()
            else:
                raise

        return obj
