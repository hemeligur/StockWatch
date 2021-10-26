from django.views.generic import TemplateView, DetailView
from django.http import Http404
from django.utils import timezone
from django.shortcuts import redirect

from datetime import timedelta
import arrow
import json

from .models import Stock, Price
from .stockdata.wrapper import StockData


class LandingPageView(TemplateView):
    template_name = "landing_page.html"


class StockSearchView(TemplateView):
    template_name = "stocks/stock_search.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if query:
            query = query.upper()
            return redirect('stocks:stock_detail', pk=query)
        else:
            return super().get(self, request, *args, **kwargs)


class StockDetailView(DetailView):
    model = Stock
    template_name = "stocks/stock_detail.html"
    context_object_name = "stock"
    stock_data = None

    def get_object(self):

        code = self.kwargs.get(self.pk_url_kwarg)

        # Tenta buscar o ativo no DB.
        # Se não encontrar, é a primeira vez que esse ativo é visualizado.
        # Então é feita uma chamada a API para criar um novo ativo.
        try:
            obj = super().get_object()

            # Atualiza o preço atual se a última atualização tiver sido há mais de 12 horas
            if obj.last_update is None or timezone.now() - obj.last_update > timedelta(hours=12):
                self.stock_data = StockData(code)

                last_date, last_prices = self.stock_data.get_last_price()
                obj.current_price = last_prices[2]  # Preço de fechamento
                obj.last_update = timezone.now()
                obj.save(update_fields=["current_price", "last_update"])

                # Salva esse novo preço no DB
                price = Price(
                    stock=code,
                    date=last_date,
                    granularity_daily=False,
                    values=last_prices
                )
                price.save()

        except Http404:
            self.stock_data = StockData(code)

            info = self.stock_data.get_info()
            if info is not None:
                obj = Stock(
                    code=code,
                    name=info['name'],
                    current_price=info['current_price'],
                    last_update=timezone.now()
                )
                obj.save()
            else:
                raise

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        code = context['stock'].code
        # Verifica se já possui os dados no DB
        now = arrow.now()
        start_date = now.replace(hour=0, minute=0, second=0).shift(months=-6)
        prices = Price.objects.filter(stock_id=code).filter(date__gte=start_date)

        if len(prices) < (now - start_date).days:
            if self.stock_data is None:
                self.stock_data = StockData(code)
            hist = self.stock_data.format_to_chart(self.stock_data.get_history())

            Price.bulk_create(hist, code)

        chart_config = {
            'data': json.dumps(hist),
            'title': json.dumps("Histórico dos últimos 6 meses"),
            'height': 800,
            'width': 2000
        }

        context['chart_config'] = chart_config
        return context
