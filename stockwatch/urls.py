from django.contrib import admin
from django.urls import path, include

from stocks.views import LandingPageView
from django.contrib.auth.views import LoginView, LogoutView
from watchers.views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name="landing_page"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('signup/', SignUpView.as_view(), name="signup"),
    path('stocks/', include("stocks.urls", namespace="stocks")),
    path('watchers/', include("watchers.urls", namespace="watchers"))
]
