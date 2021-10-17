from django.urls import path
from .views import WatcherListView, WatcherCreateView, WatcherDetailView, WatcherUpdateView, WatcherDeleteView

app_name = "watchers"

urlpatterns = [
    path('', WatcherListView.as_view(), name="watcher_list"),
    path('create/', WatcherCreateView.as_view(), name="watcher_create"),
    path('create/<pk>/', WatcherCreateView.as_view(), name="watcher_create"),
    path('<int:pk>/', WatcherDetailView.as_view(), name="watcher_detail"),
    path('<int:pk>/update', WatcherUpdateView.as_view(), name="watcher_update"),
    path('<int:pk>/delete', WatcherDeleteView.as_view(), name="watcher_delete")
]
