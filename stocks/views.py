from django.views.generic import TemplateView, DetailView
from django.http import Http404
from django.utils import timezone
from django.shortcuts import redirect

from datetime import timedelta

from .models import Stock
from .stockdata.wrapper import StockData


class LandingPageView(TemplateView):
    template_name = "landing_page.html"


class StockSearchView(TemplateView):
    template_name = "stocks/stock_search.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if query:
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

            # Atualiza o preço atual se a última atualização tiver sido há mais de 1 dia
            if obj.last_update is None or timezone.now() - obj.last_update > timedelta(days=1):
                self.stock_data = StockData(code)

                obj.current_price = self.stock_data.get_last_price()
                obj.last_update = timezone.now()
                obj.save()

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
