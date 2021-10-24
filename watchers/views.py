from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm
from .models import Watcher
from stocks.models import Stock


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy('login')


class WatcherListView(LoginRequiredMixin, ListView):
    model = Watcher
    template_name = "watchers/watcher_list.html"
    context_object_name = "watchers"

    def get_queryset(self):
        user = self.request.user
        return Watcher.objects.filter(user=user)


class WatcherCreateView(LoginRequiredMixin, CreateView):
    model = Watcher
    template_name = "watchers/watcher_create.html"
    fields = [
        "upper_threshold",
        "lower_threshold",
        "interval"
    ]
    success_url = reverse_lazy('watchers:watcher_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.stock = Stock.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)


class WatcherDetailView(LoginRequiredMixin, DetailView):
    model = Watcher
    template_name = "watchers/watcher_detail.html"
    context_object_name = "watcher"

    def get_queryset(self):
        user = self.request.user
        return Watcher.objects.filter(user=user)


class WatcherUpdateView(LoginRequiredMixin, UpdateView):
    model = Watcher
    template_name = "watchers/watcher_update.html"
    fields = [
        "upper_threshold",
        "lower_threshold",
        "interval"
    ]
    success_url = reverse_lazy('watchers:watcher_list')

    def get_queryset(self):
        user = self.request.user
        return Watcher.objects.filter(user=user)


class WatcherDeleteView(LoginRequiredMixin, DeleteView):
    model = Watcher
    template_name = "watchers/watcher_delete.html"
    context_object_name = "watcher"
    success_url = reverse_lazy('watchers:watcher_list')

    def get_queryset(self):
        user = self.request.user
        return Watcher.objects.filter(user=user)
