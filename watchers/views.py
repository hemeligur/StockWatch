from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from .models import Watcher

# from stocks.stockdata.wrapper import StockData


class WatcherListView(ListView):
    model = Watcher
    template_name = "watchers/watcher_list.html"
    context_object_name = "watchers"


class WatcherCreateView(CreateView):
    model = Watcher
    template_name = "watchers/watcher_create.html"
    fields = [
        "stock",
        "upper_threshold",
        "lower_threshold",
        "interval"
    ]
    success_url = reverse_lazy('watchers:watcher_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        return super().form_valid(form)


class WatcherDetailView(DetailView):
    model = Watcher
    template_name = "watchers/watcher_detail.html"
    context_object_name = "watcher"


class WatcherUpdateView(UpdateView):
    model = Watcher
    template_name = "watchers/watcher_update.html"
    fields = [
        "upper_threshold",
        "lower_threshold",
        "interval"
    ]
    success_url = reverse_lazy('watchers:watcher_list')


class WatcherDeleteView(DeleteView):
    model = Watcher
    template_name = "watchers/watcher_delete.html"
    context_object_name = "watcher"
    success_url = reverse_lazy('watchers:watcher_list')
