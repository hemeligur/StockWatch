from django.contrib import admin
from django.urls import path, include

from stocks.views import LandingPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name="landing_page"),
    path('stocks/', include("stocks.urls", namespace="stocks")),
    path('watchers/', include("watchers.urls", namespace="watchers"))
]
